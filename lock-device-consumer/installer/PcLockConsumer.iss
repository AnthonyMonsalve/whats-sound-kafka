; PcLockConsumer.iss (ADMIN / Program Files)

#define MyAppName "PC Lock Consumer"
#define MyAppVersion "1.0.0"
#define MyAppExeName "pc-lock-consumer.exe"

[Setup]
AppId={{A6C5F4C7-33B8-46C4-901C-7D77E74C5F2B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={pf}\PcLockConsumer
DefaultGroupName={#MyAppName}
OutputDir=.
OutputBaseFilename=PcLockConsumerSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Files]
Source: "..\dist-bundle\pc-lock-consumer.exe"; DestDir: "{app}"; Flags: ignoreversion
; Copiar .env solo si NO existe (para no machacar config en upgrades)
Source: "..\dist-bundle\.env"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "..\dist-bundle\install_task.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist-bundle\uninstall_task.ps1"; DestDir: "{app}"; Flags: ignoreversion

[Run]
; Crea/actualiza la tarea programada (oculto)
Filename: "powershell.exe"; \
  Parameters: "-ExecutionPolicy Bypass -File ""{app}\install_task.ps1"" -ExePath ""{app}\{#MyAppExeName}"" -WorkDir ""{app}"" -TaskName ""PC Lock Consumer"""; \
  Flags: runhidden waituntilterminated; \
  StatusMsg: "Creando la tarea programada..."

[UninstallRun]
; Elimina la tarea al desinstalar
Filename: "powershell.exe"; \
  Parameters: "-ExecutionPolicy Bypass -File ""{app}\uninstall_task.ps1"" -TaskName ""PC Lock Consumer"""; \
  Flags: runhidden waituntilterminated

[Icons]
Name: "{group}\Ver logs"; Filename: "notepad.exe"; Parameters: """{app}\logs\consumer.log"""; WorkingDir: "{app}"
