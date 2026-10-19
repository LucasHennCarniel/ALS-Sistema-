; ==========================================================
; SISTEMA ALS - SCRIPT OFICIAL DE INSTALACAO (INNO SETUP 6)
; ==========================================================

#define MyAppName "Sistema ALS"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "ALS Transportes"
#define MyAppExeName "SistemaManutencaoALS.exe"

[Setup]
; Identificador unico do aplicativo
AppId={{C8E19B34-3A18-49A5-9276-8051E7728B4E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName=C:\Sistema ALS
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist_installer
OutputBaseFilename=Instalador_SistemaALS_Setup
SetupIconFile=img\logo ALS.ico
UninstallDisplayIcon={app}\img\logo ALS.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
CloseApplications=force
RestartApplications=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Dirs]
; Garante a existencia das pastas padrao da estrutura com permissoes de usuario
Name: "{app}\data"; Permissions: users-full
Name: "{app}\backup"; Permissions: users-full
Name: "{app}\output"; Permissions: users-full
Name: "{app}\img"; Permissions: users-full

[Files]
; Executavel principal compilado
Source: "SistemaALS_Atualizado\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Imagens e icones oficiais da ALS
Source: "SistemaALS_Atualizado\img\*"; DestDir: "{app}\img"; Flags: ignoreversion recursesubdirs createallsubdirs

; Banco de dados inicial (A flag 'onlyifdoesntexist' garante que reinstalacoes NAO sobrescrevam dados reais)
Source: "SistemaALS_Atualizado\data\sistema_als.db"; DestDir: "{app}\data"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\img\logo ALS.ico"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\img\logo ALS.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\img\logo ALS.ico"

[Run]
; Instalacao interativa: oferece abrir o sistema ao final
Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent
; Atualizacao automatica (silenciosa): reabre o sistema sem intervencao do usuario
Filename: "{app}\{#MyAppExeName}"; Flags: nowait; Check: WizardSilent
