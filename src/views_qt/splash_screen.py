"""
Janela de Inicializacao Unificada em Fluent Design
Uma unica janela conduz: checagem de atualizacao -> aviso da nova versao -> download -> instalacao.
"""
import logging
import os
import sys
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QStackedWidget, QApplication
from qfluentwidgets import (
    IndeterminateProgressBar, ProgressBar, TitleLabel, SubtitleLabel, BodyLabel,
    CaptionLabel, PushButton, PrimaryPushButton, setThemeColor
)

from src.config import APP_VERSION, BASE_PATH
from src.services.updater_service import (
    CheckUpdateThread, DownloadUpdateThread, UpdaterService, UpdateInfo,
    pasta_atualizacao, NOME_INSTALADOR
)

# Etapas (indices do QStackedWidget) e altura da janela em cada uma
ETAPA_CHECANDO, ETAPA_AVISO, ETAPA_DOWNLOAD = 0, 1, 2
ALTURAS = {ETAPA_CHECANDO: 320, ETAPA_AVISO: 540, ETAPA_DOWNLOAD: 380}
TIMEOUT_CHECAGEM_MS = 6000
INTERVALO_MONITOR_MS = 500
TIMEOUT_INICIO_INSTALADOR_MS = 180_000   # antivírus pode levar um tempo escaneando o instalador de ~320 MB
INTERVALO_ESPERA_MS = 1000
TIMEOUT_ESPERA_INSTALACAO_MS = 15 * 60 * 1000
COR_TEXTO_SUAVE = "#94A3B8"


def _caminho_logo():
    candidatos = [
        os.path.join(BASE_PATH, "img", "logo ALS.png"),
        os.path.join(getattr(sys, "_MEIPASS", ""), "img", "logo ALS.png"),
        os.path.abspath(os.path.join("img", "logo ALS.png")),
    ]
    return next((c for c in candidatos if os.path.exists(c)), None)


class ModernSplashScreen(QWidget):
    """Splash + fluxo de atualizacao em uma unica janela"""
    concluido = Signal(object)  # Emite UpdateInfo (adiada pelo usuario) ou None. Apenas uma vez.

    def __init__(self, token=None, parent=None, update_info=None):
        """update_info: abre direto no aviso da nova versao (lembrete do menu), sem checar de novo"""
        super().__init__(parent)
        self.token = token
        self.update_info = None
        self._emitido = False
        self._acao_tentar = None
        self._processo = None
        self._init_ui()
        if update_info is not None:
            self._mostrar_aviso(update_info)
        else:
            pendente = UpdaterService.instalacao_em_andamento(versao_atual=APP_VERSION)
            if pendente:
                self._aguardar_instalacao(pendente)
            else:
                self._iniciar_checagem()

    # ------------------------------------------------------------------ UI
    def _init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(480, ALTURAS[ETAPA_CHECANDO])

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(20, 20, 20, 20)

        # O seletor por objectName evita que bordas/fundo se apliquem a todos os filhos
        self.card = QWidget(self)
        self.card.setObjectName("cardSplash")
        self.card.setStyleSheet("""
            QWidget#cardSplash {
                background-color: #1E2227;
                border: 1px solid #333842;
                border-radius: 16px;
            }
        """)
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(10)

        self.lbl_logo = QLabel(self.card)
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        logo = _caminho_logo()
        if logo:
            self.lbl_logo.setPixmap(QPixmap(logo).scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.lbl_logo)

        self.lbl_titulo = TitleLabel("Sistema ALS", self.card)
        self.lbl_titulo.setAlignment(Qt.AlignCenter)
        self.lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #F1F5F9;")
        layout.addWidget(self.lbl_titulo)

        self.lbl_status = CaptionLabel("Inicializando e verificando atualizações...", self.card)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(f"color: {COR_TEXTO_SUAVE}; font-size: 12px;")
        layout.addWidget(self.lbl_status)

        self.etapas = QStackedWidget(self.card)
        self.etapas.addWidget(self._criar_etapa_checando())
        self.etapas.addWidget(self._criar_etapa_aviso())
        self.etapas.addWidget(self._criar_etapa_download())
        layout.addWidget(self.etapas, stretch=1)

        raiz.addWidget(self.card)

    def _criar_etapa_checando(self):
        pagina = QWidget()
        lay = QVBoxLayout(pagina)
        lay.setContentsMargins(0, 8, 0, 0)
        self.barra_indeterminada = IndeterminateProgressBar(pagina)
        self.barra_indeterminada.setFixedWidth(340)
        lay.addWidget(self.barra_indeterminada, alignment=Qt.AlignCenter)
        lay.addStretch()
        return pagina

    def _criar_etapa_aviso(self):
        pagina = QWidget()
        lay = QVBoxLayout(pagina)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(8)

        self.lbl_aviso_titulo = SubtitleLabel("Nova Versão Disponível", pagina)
        self.lbl_aviso_titulo.setStyleSheet("color: #F1F5F9; font-weight: bold;")
        lay.addWidget(self.lbl_aviso_titulo)

        self.lbl_aviso_msg = BodyLabel("", pagina)
        self.lbl_aviso_msg.setWordWrap(True)
        self.lbl_aviso_msg.setStyleSheet("color: #CBD5E1; font-size: 13px;")
        lay.addWidget(self.lbl_aviso_msg)

        rotulo_notas = CaptionLabel("O que mudou nesta versão:", pagina)
        rotulo_notas.setStyleSheet(f"color: {COR_TEXTO_SUAVE};")
        lay.addWidget(rotulo_notas)
        self.txt_notas = QTextEdit(pagina)
        self.txt_notas.setReadOnly(True)
        self.txt_notas.setStyleSheet("""
            QTextEdit {
                background-color: #14171B;
                border: 1px solid #333842;
                border-radius: 8px;
                padding: 8px;
                color: #E2E8F0;
                font-size: 12px;
            }
        """)
        lay.addWidget(self.txt_notas, stretch=1)

        botoes = QHBoxLayout()
        botoes.addStretch()
        self.btn_depois = PushButton("Lembrar Mais Tarde", pagina)
        self.btn_depois.clicked.connect(self._on_depois)
        self.btn_atualizar = PrimaryPushButton("Atualizar Sistema Agora", pagina)
        self.btn_atualizar.setStyleSheet("background-color: #4CAF50; border-color: #4CAF50;")
        self.btn_atualizar.clicked.connect(self._iniciar_download)
        botoes.addWidget(self.btn_depois)
        botoes.addWidget(self.btn_atualizar)
        lay.addLayout(botoes)
        return pagina

    def _criar_etapa_download(self):
        pagina = QWidget()
        lay = QVBoxLayout(pagina)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(10)

        self.barra_download = ProgressBar(pagina)
        self.barra_download.setValue(0)
        lay.addWidget(self.barra_download)

        self.lbl_download_info = CaptionLabel(
            "Um backup do banco é feito antes. Seus dados não serão apagados.", pagina
        )
        self.lbl_download_info.setAlignment(Qt.AlignCenter)
        self.lbl_download_info.setWordWrap(True)
        self.lbl_download_info.setStyleSheet(f"color: {COR_TEXTO_SUAVE};")
        lay.addWidget(self.lbl_download_info)

        # Botoes exibidos apenas se o download falhar
        self.linha_erro = QWidget(pagina)
        erro_lay = QHBoxLayout(self.linha_erro)
        erro_lay.setContentsMargins(0, 0, 0, 0)
        erro_lay.addStretch()
        self.btn_erro_sair = PushButton("Continuar sem atualizar", self.linha_erro)
        self.btn_erro_sair.clicked.connect(self._on_depois)
        self.btn_erro_tentar = PrimaryPushButton("Tentar novamente", self.linha_erro)
        self.btn_erro_tentar.setStyleSheet("background-color: #4CAF50; border-color: #4CAF50;")
        self.btn_erro_tentar.clicked.connect(self._tentar_novamente)
        erro_lay.addWidget(self.btn_erro_sair)
        erro_lay.addWidget(self.btn_erro_tentar)
        self.linha_erro.hide()
        lay.addWidget(self.linha_erro)
        lay.addStretch()
        return pagina

    def _ir_para(self, etapa):
        self.etapas.setCurrentIndex(etapa)
        self.setFixedSize(480, ALTURAS[etapa])
        tela = QApplication.primaryScreen()
        if tela:
            self.move(tela.availableGeometry().center() - self.rect().center())

    # ----------------------------------------------------- Etapa 1: checagem
    def _iniciar_checagem(self):
        setThemeColor('#4CAF50')
        self.thread = CheckUpdateThread(self.token, self)
        self.thread.resultado.connect(self._on_resultado)
        self.thread.start()

        # Seguranca: se a rede travar, abre o sistema sem atualizacao
        self.timer_timeout = QTimer(self)
        self.timer_timeout.setSingleShot(True)
        self.timer_timeout.timeout.connect(self._on_timeout)
        self.timer_timeout.start(TIMEOUT_CHECAGEM_MS)

    def _on_timeout(self):
        if self.etapas.currentIndex() == ETAPA_CHECANDO:
            self._finalizar(None)

    def _on_resultado(self, info: UpdateInfo):
        if self._emitido or self.etapas.currentIndex() != ETAPA_CHECANDO:
            return
        self.timer_timeout.stop()
        if info is not None and info.disponivel:
            self._mostrar_aviso(info)
        else:
            # Pequeno atraso estetico para a animacao rodar de forma fluida
            QTimer.singleShot(400, lambda: self._finalizar(None))

    # ------------------------------------------------------ Etapa 2: aviso
    def _mostrar_aviso(self, info: UpdateInfo):
        self.update_info = info
        if info.obrigatoria:
            self.lbl_aviso_titulo.setText("Atualização Obrigatória")
            self.lbl_aviso_titulo.setStyleSheet("color: #F87171; font-weight: bold;")
            self.btn_depois.setText("Fechar Sistema")
        else:
            self.lbl_aviso_titulo.setText("Nova Versão Disponível")
            self.lbl_aviso_titulo.setStyleSheet("color: #F1F5F9; font-weight: bold;")
            self.btn_depois.setText("Lembrar Mais Tarde")
        self.lbl_status.setText(f"Versão atual: v{APP_VERSION}  →  nova versão: {info.versao}")
        msg = f"A versão {info.versao} está pronta para instalação."
        if info.obrigatoria:
            msg += " Ela contém alterações essenciais; é necessário atualizar para continuar."
        self.lbl_aviso_msg.setText(msg)
        self.txt_notas.setPlainText(info.notas_versao)
        self._ir_para(ETAPA_AVISO)

    def _on_depois(self):
        if self.update_info is not None and self.update_info.obrigatoria:
            QApplication.instance().quit()
            self.close()
            return
        self._finalizar(self.update_info)

    # --------------------------------------------------- Etapa 3: download
    def _limpar_erro(self, texto):
        self.lbl_status.setText(texto)
        self.lbl_status.setStyleSheet(f"color: {COR_TEXTO_SUAVE}; font-size: 12px;")
        self.linha_erro.hide()

    def _mostrar_erro(self, mensagem):
        """Mostra o motivo real da falha e as opções (tentar de novo / continuar). Nunca deixa a janela muda."""
        logging.error("Atualizacao: %s", mensagem)
        self.lbl_status.setText(mensagem)
        self.lbl_status.setStyleSheet("color: #F87171; font-size: 12px;")
        self.btn_erro_sair.setText("Fechar Sistema" if self.update_info.obrigatoria else "Continuar sem atualizar")
        self.linha_erro.show()
        self._ir_para(ETAPA_DOWNLOAD)

    def _tentar_novamente(self):
        if self._acao_tentar is not None:
            self._acao_tentar()

    def _iniciar_download(self):
        self._acao_tentar = self._iniciar_download
        self._limpar_erro("Baixando nova versão...")
        self.barra_download.setValue(0)
        self._ir_para(ETAPA_DOWNLOAD)

        destino = os.path.join(pasta_atualizacao(), NOME_INSTALADOR)
        self.thread_download = DownloadUpdateThread(
            download_url=self.update_info.download_url,
            destino_path=destino,
            token=self.token,
            parent=self,
            tamanho_esperado=self.update_info.tamanho_bytes,
        )
        self.thread_download.progresso.connect(self._on_progresso)
        self.thread_download.sucesso.connect(self._on_download_ok)
        self.thread_download.falha.connect(self._on_download_falha)
        self.thread_download.start()

    def _on_progresso(self, pct: int):
        self.barra_download.setValue(pct)
        self.lbl_status.setText(f"Baixando nova versão: {pct}% concluído...")

    def _on_download_ok(self, caminho_instalador: str):
        self._caminho_instalador = caminho_instalador
        self.barra_download.setValue(100)
        self._limpar_erro("Download concluído! Iniciando o instalador...")
        self.lbl_download_info.setText("Não feche esta janela nem abra o sistema de novo. Ele reabrirá sozinho.")
        QTimer.singleShot(500, self._iniciar_instalador)

    def _on_download_falha(self, mensagem: str):
        self._acao_tentar = self._iniciar_download
        self._mostrar_erro(mensagem)

    # ----------------------------------------- Etapa 4: instalador em execucao
    def _iniciar_instalador(self):
        """Dispara o instalador e só encerra o app depois de confirmar que ele realmente iniciou"""
        self._acao_tentar = self._iniciar_instalador
        self._limpar_erro("Iniciando o instalador...")
        try:
            self._processo, self._log_instalador = UpdaterService.iniciar_instalador(
                self._caminho_instalador, self.update_info.versao
            )
        except Exception as e:
            logging.exception("Falha ao iniciar o instalador")
            self._mostrar_erro(
                f"Não foi possível iniciar o instalador: {e}. "
                f"Você pode executá-lo manualmente: {self._caminho_instalador}"
            )
            return
        self._tempo_instalador = 0
        self.timer_instalador = QTimer(self)
        self.timer_instalador.setInterval(INTERVALO_MONITOR_MS)
        self.timer_instalador.timeout.connect(self._monitorar_instalador)
        self.timer_instalador.start()

    def _monitorar_instalador(self):
        self._tempo_instalador += INTERVALO_MONITOR_MS
        codigo = self._processo.poll()
        log_iniciado = os.path.exists(self._log_instalador) and os.path.getsize(self._log_instalador) > 0

        if codigo not in (None, 0):
            self.timer_instalador.stop()
            UpdaterService.limpar_marcador_instalacao()
            self._mostrar_erro(
                f"O instalador terminou com erro (código {codigo}). Detalhes em: {self._log_instalador}"
            )
        elif codigo == 0 or log_iniciado:
            # O instalador já está trabalhando: pode encerrar o app para ele trocar os arquivos
            self.timer_instalador.stop()
            self.lbl_status.setText("Instalando a atualização... o sistema reabrirá sozinho em instantes.")
            QTimer.singleShot(1500, UpdaterService.finalizar_para_instalacao)
        elif self._tempo_instalador >= TIMEOUT_INICIO_INSTALADOR_MS:
            self.timer_instalador.stop()
            UpdaterService.limpar_marcador_instalacao()
            self._mostrar_erro(
                "O instalador não iniciou em 3 minutos (o antivírus pode estar verificando o arquivo). "
                f"Você pode executá-lo manualmente: {self._caminho_instalador}"
            )
        else:
            segundos = self._tempo_instalador // 1000
            self.lbl_status.setText(f"Aguardando o instalador iniciar... ({segundos}s)")

    # ------------------------------ Instalacao iniciada antes (app reaberto)
    def _aguardar_instalacao(self, dados):
        """Há um instalador rodando: não abre o app no meio da troca de arquivos, espera terminar"""
        logging.info("Instalacao em andamento (pid=%s, versao=%s): aguardando", dados.get("pid"), dados.get("versao"))
        self._dados_instalacao = dados
        self._espera_ms = 0
        self.lbl_status.setText(
            f"A atualização para {dados.get('versao', 'nova versão')} está sendo instalada. "
            "Aguarde: o sistema abrirá sozinho."
        )
        self.timer_espera = QTimer(self)
        self.timer_espera.setInterval(INTERVALO_ESPERA_MS)
        self.timer_espera.timeout.connect(self._verificar_instalacao)
        self.timer_espera.start()

    def _verificar_instalacao(self):
        self._espera_ms += INTERVALO_ESPERA_MS
        if (UpdaterService.instalacao_em_andamento(versao_atual=APP_VERSION) is not None
                and self._espera_ms < TIMEOUT_ESPERA_INSTALACAO_MS):
            return
        self.timer_espera.stop()
        concluiu = UpdaterService.instalacao_foi_concluida(self._dados_instalacao.get("log", ""))
        UpdaterService.limpar_marcador_instalacao()
        if concluiu:
            # O instalador já abriu a versão nova: esta cópia antiga só precisa sair
            self.lbl_status.setText("Atualização concluída! Reabrindo o sistema...")
            QTimer.singleShot(1500, UpdaterService.finalizar_para_instalacao)
        else:
            logging.warning("Instalador terminou sem confirmar sucesso; abrindo normalmente")
            self._iniciar_checagem()

    # ------------------------------------------------------------- Saida
    def _finalizar(self, info):
        """Entrega o controle ao app principal. Executa uma unica vez."""
        if self._emitido:
            return
        self._emitido = True
        if hasattr(self, "timer_timeout"):
            self.timer_timeout.stop()
        self.concluido.emit(info)
        self.close()
