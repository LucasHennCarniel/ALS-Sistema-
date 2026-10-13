@echo off
chcp 65001 >nul
title Sistema ALS - Painel de Controle (Windows 11 Fluent)
color 0B

:MENU
cls
echo.
echo ==========================================================
echo       SISTEMA ALS - PAINEL DE CONTROLE E BUILD
echo ==========================================================
echo.
echo   Escolha uma opcao:
echo.
echo   [1] Iniciar Sistema Agora (Interface Moderna Fluent)
echo   [2] Gerar/Atualizar Executavel (.exe)
echo   [3] Gerar Instalador Oficial do Windows (Setup.exe)
echo   [0] Sair
echo.
echo ==========================================================
set /p opcao="Digite o numero da opcao: "

if "%opcao%"=="1" goto INICIAR
if "%opcao%"=="2" goto GERAR_EXE
if "%opcao%"=="3" goto GERAR_INSTALADOR
if "%opcao%"=="0" goto SAIR

echo.
echo Opcao invalida!
timeout /t 2 >nul
goto MENU


:INICIAR
cls
echo.
echo Iniciando Sistema ALS (Fluent Design)...
call :VERIFICAR_TODAS_DEPENDENCIAS
echo.
echo Executando sistema...
python src\main.py
if errorlevel 1 (
    echo.
    echo O programa encontrou um erro. Verifique acima.
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
echo   - Verificar e garantir as dependencias
echo   - Limpar cache antigo
echo   - Compilar a aplicacao com SQLAlchemy e Streamlit
echo   - Atualizar a pasta SistemaALS_Atualizado
echo.
pause

call :VERIFICAR_TODAS_DEPENDENCIAS

echo Limpando cache antigo...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul

echo.
echo Compilando... (aguarde de 1 a 2 minutos)
pyinstaller --noconfirm --onefile --windowed ^
    --name "SistemaManutencaoALS" ^
    --icon="img/logo ALS.png" ^
    --add-data "img;img" ^
    --add-data "src;src" ^
    --collect-all "streamlit" ^
    --collect-all "plotly" ^
    --hidden-import "PySide6" ^
    --hidden-import "qfluentwidgets" ^
    --hidden-import "openpyxl" ^
    --hidden-import "reportlab" ^
    --hidden-import "PIL" ^
    --hidden-import "pandas" ^
    --hidden-import "sqlalchemy" ^
    --hidden-import "sqlalchemy.dialects.sqlite" ^
    --hidden-import "docx" ^
    --log-level WARN src\main.py

if errorlevel 1 (
    echo.
    echo Erro ao gerar executavel!
    pause
    goto MENU
)

echo.
echo Atualizando pasta final...
set "PASTA_DIST=SistemaALS_Atualizado"
if not exist "%PASTA_DIST%" mkdir "%PASTA_DIST%"
if not exist "%PASTA_DIST%\data" mkdir "%PASTA_DIST%\data"
if not exist "%PASTA_DIST%\img" mkdir "%PASTA_DIST%\img"
if not exist "%PASTA_DIST%\backup" mkdir "%PASTA_DIST%\backup"
if not exist "%PASTA_DIST%\output" mkdir "%PASTA_DIST%\output"

move /Y "dist\SistemaManutencaoALS.exe" "%PASTA_DIST%\" >nul 2>&1
if exist "data\sistema_als.db" copy /Y "data\sistema_als.db" "%PASTA_DIST%\data\sistema_als.db" >nul
xcopy "img\*.*" "%PASTA_DIST%\img\" /E /I /Y /Q >nul 2>&1

echo.
echo Concluido com Sucesso! A pasta '%PASTA_DIST%' esta atualizada.
echo.
pause
goto MENU


:GERAR_INSTALADOR
cls
echo.
echo ==========================================================
echo        GERANDO INSTALADOR OFICIAL DO WINDOWS (SETUP)
echo ==========================================================
echo.
if not exist "SistemaALS_Atualizado\SistemaManutencaoALS.exe" (
    echo O executavel 'SistemaALS_Atualizado\SistemaManutencaoALS.exe' nao foi encontrado.
    echo Gerando o executavel primeiro...
    pause
    goto GERAR_EXE
)

:: Localizacao automatica do compilador Inno Setup 6
set "ISCC="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    where iscc >nul 2>&1
    if not errorlevel 1 set "ISCC=iscc"
)

if "%ISCC%"=="" (
    echo.
    echo ERRO: Compilador Inno Setup 6 nao encontrado!
    echo Instale o Inno Setup executando no terminal: winget install JRSoftware.InnoSetup
    pause
    goto MENU
)

echo Compilador encontrado: %ISCC%
echo.
echo Compilando instalador oficial... (aguarde cerca de 40 segundos)
"%ISCC%" installer.iss

if errorlevel 1 (
    echo.
    echo ERRO ao compilar o instalador Inno Setup!
    pause
    goto MENU
)

echo.
echo ==========================================================
echo   Instalador gerado com Sucesso em 'dist_installer\'!
echo ==========================================================
echo.
set /p abrir="Deseja abrir a pasta do instalador agora? (S/N): "
if /i "%abrir%"=="S" explorer "dist_installer"
goto MENU


:VERIFICAR_TODAS_DEPENDENCIAS
echo Verificando dependencias...
call :CHECK_DEP PySide6 PySide6
call :CHECK_DEP qfluentwidgets PySide6-Fluent-Widgets
call :CHECK_DEP pandas pandas
call :CHECK_DEP openpyxl openpyxl
call :CHECK_DEP sqlalchemy sqlalchemy
call :CHECK_DEP streamlit streamlit
call :CHECK_DEP plotly plotly
call :CHECK_DEP reportlab reportlab
call :CHECK_DEP PIL pillow
call :CHECK_DEP docx python-docx
call :CHECK_DEP PyInstaller pyinstaller
goto :eof

:CHECK_DEP
set "MODULO=%~1"
set "PACOTE=%~2"
python -c "import %MODULO%" >nul 2>&1
if errorlevel 1 (
    echo   [-] %MODULO% nao encontrado. Instalando %PACOTE%...
    pip install %PACOTE%
) else (
    echo   [OK] %MODULO% pronto.
)
goto :eof

:SAIR
exit
