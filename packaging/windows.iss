#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppId={{7A7C58E3-7D83-4AB7-95C9-7D55C9C532D1}
AppName=GuihGuih Cyber
AppVersion={#AppVersion}
AppPublisher=GuihInc
DefaultDirName={localappdata}\Programs\GuihGuih Cyber
DefaultGroupName=GuihGuih Cyber
OutputDir=dist
OutputBaseFilename=GuihGuihCyber-Setup
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\GuihGuihCyber.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\GuihGuihCyber.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\GuihGuih Cyber"; Filename: "{app}\GuihGuihCyber.exe"
Name: "{autodesktop}\GuihGuih Cyber"; Filename: "{app}\GuihGuihCyber.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked

[Run]
Filename: "{app}\GuihGuihCyber.exe"; Description: "Abrir GuihGuih Cyber"; Flags: postinstall nowait skipifsilent

