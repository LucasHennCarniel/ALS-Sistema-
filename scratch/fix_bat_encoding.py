import codecs

bat_content = """@echo off
chcp 65001 >nul
title Sistema ALS - Painel de Controle
color 0B

:MENU
cls
echo.
echo ==========================================================
echo                   SISTEMA ALS - PAINEL
echo ==========================================================
echo.
echo   Escolha uma opcao:
echo.
echo   [1] Iniciar Sistema Agora (Abre direto para uso)
echo   [2] Gerar/Atualizar Executavel (.exe)
echo   [0] Sair
echo.
echo ==========================================================
set /p opcao="Digite o numero da opcao: "

if "%opcao%"=="1" goto INICIAR
if "%opcao%"=="2" goto GERAR_EXE
if "%opcao%"=="0" goto SAIR

echo.
echo Opcao invalida!
timeout /t 2 >nul
goto MENU


:INICIAR
cls
echo.
echo Iniciando Sistema ALS...
echo Verificando dependencias...
python -c "import pandas, tkcalendar, openpyxl, reportlab" 2>nul
if errorlevel 1 (
    echo Instalando pacotes necessarios...
    pip install pandas openpyxl reportlab tkcalendar pillow >nul
)
echo.
python src\main.py
if errorlevel 1 (
    echo.
    echo O programa encontrou um erro. Verifique a janela.
    pause
)
goto MENU


:GERAR_EXE
cls
echo.
echo ==========================================================
echo              GERANDO EXECUTAVEL DO SISTEMA
echo ==========================================================
echo.
echo  Este processo vai:
echo   - Limpar cache antigo
echo   - Compilar o codigo atual
echo   - Criar a pasta SistemaALS_Atualizado
echo.
echo  Tempo estimado: 1 minuto.
echo.
pause

echo Limpando cache antigo...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul

echo.
echo Compilando... (aguarde)
pyinstaller --noconfirm --onefile --windowed --name "SistemaManutencaoALS" --icon="img/logo ALS.png" --add-data "img;img" --hidden-import "openpyxl" --hidden-import "reportlab" --hidden-import "PIL" --hidden-import "pandas" --hidden-import "tkcalendar" --log-level WARN src/main.py

if errorlevel 1 (
    echo.
    echo Erro ao gerar executavel!
    pause
    goto MENU
)

echo.
echo Criando pasta final...
set "PASTA_DIST=SistemaALS_Atualizado"
if exist "%PASTA_DIST%" rmdir /s /q "%PASTA_DIST%" 2>nul
mkdir "%PASTA_DIST%"
mkdir "%PASTA_DIST%\data"
mkdir "%PASTA_DIST%\img"

echo Copiando arquivos...
move "dist\SistemaManutencaoALS.exe" "%PASTA_DIST%\" >nul 2>&1
if exist "data\sistema_als.db" copy /Y "data\sistema_als.db" "%PASTA_DIST%\data\sistema_als.db" >nul
xcopy "img\*.*" "%PASTA_DIST%\img\" /E /I /Y /Q >nul 2>&1

echo.
echo Concluido com Sucesso! A pasta '%PASTA_DIST%' esta pronta.
echo.
set /p abrir="Deseja abrir a pasta gerada agora? (S/N): "
if /i "%abrir%"=="S" explorer "%PASTA_DIST%"
goto MENU

:SAIR
exit
"""

with codecs.open('SISTEMA_ALS.bat', 'w', encoding='cp1252') as f:
    f.write(bat_content)
