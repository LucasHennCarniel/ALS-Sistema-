from src.models.veiculo_model import VeiculoModel
import logging

class VeiculoController:
    """
    Controlador para gerenciar lógicas de negócio de Veículos
    """
    
    def __init__(self, model=None):
        self.model = model or VeiculoModel()
        
    def obter_todos(self):
        return self.model.obter_todos()
        
    def obter_veiculo_por_placa(self, placa):
        return self.model.obter_por_placa(placa)
        
    def obter_veiculos_ativos_formatado(self):
        """Retorna lista formatada 'PLACA - TIPO - DESCRICAO' para comboboxes"""
        ativos = self.model.obter_ativos()
        lista = []
        for v in ativos:
            texto = f"{v['placa']} - {v['tipo_veiculo']}"
            if v['descricao']:
                texto += f" - {v['descricao']}"
            lista.append(texto)
        return lista
        
    def extrair_placa_da_selecao(self, texto_selecao):
        """Extrai a placa do texto selecionado no combobox"""
        if ' - ' in texto_selecao:
            return texto_selecao.split(' - ')[0].strip()
        return texto_selecao.strip()
        
    def adicionar_veiculo(self, tipo, placa, descricao='', km_inicial=0):
        placa = placa.upper().strip()
        tipo = tipo.upper().strip() if tipo else 'OUTRO'
        if not placa:
            return False, "A Placa é obrigatória!"
            
        try:
            if self.model.obter_por_placa(placa):
                return False, "Placa já cadastrada!"
                
            km_inicial = float(km_inicial) if km_inicial else 0
            self.model.inserir(tipo, placa, descricao, km_inicial)
            return True, "Veículo cadastrado com sucesso!"
        except Exception as e:
            logging.error(f"Erro ao cadastrar veiculo: {e}")
            return False, f"Erro ao cadastrar veículo: {e}"
            
    def atualizar_veiculo(self, placa_antiga, tipo, nova_placa, descricao, ativo, ultima_km=None):
        nova_placa = nova_placa.upper().strip()
        placa_antiga = placa_antiga.upper().strip()
        tipo = tipo.upper().strip() if tipo else 'OUTRO'
        
        if not nova_placa:
            return False, "A Placa é obrigatória!"
            
        try:
            if nova_placa != placa_antiga and self.model.obter_por_placa(nova_placa):
                return False, "A nova placa já está cadastrada em outro veículo!"
                
            self.model.atualizar(placa_antiga, tipo, nova_placa, descricao, ativo, ultima_km=ultima_km)
            return True, "Veículo atualizado com sucesso!"
        except Exception as e:
            logging.error(f"Erro ao atualizar veiculo: {e}")
            return False, f"Erro ao atualizar veículo: {e}"
            
    def excluir_veiculo(self, placa):
        try:
            sucesso = self.model.deletar(placa)
            if sucesso:
                return True, "Veículo excluído com sucesso!"
            return False, "Veículo não encontrado."
        except Exception as e:
            logging.error(f"Erro ao excluir veiculo: {e}")
            return False, f"Erro ao excluir veículo: {e}"
            
    def atualizar_km(self, placa, nova_km):
        try:
            nova_km = float(nova_km)
            return self.model.atualizar_km(placa, nova_km)
        except Exception as e:
            logging.error(f"Erro ao atualizar km: {e}")
            return False
            
    def obter_estatisticas(self):
        return self.model.obter_estatisticas()
