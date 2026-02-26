#define MyAppName      "C-BOM"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "C-BOM Team"
#define MyAppURL       "https://github.com/your-org/c-bom"
#define MyAppExeName   "C-BOM.exe"
#define MyAppDescription "Cryptographic Bill of Materials Management Tool"

[Setup]
AppId={{A3F2B7C1-4D8E-4F9A-B2C3-D4E5F6A7B8C9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=dist
OutputBaseFilename=C-BOM-Setup-v{#MyAppVersion}
SetupIconFile=cbom.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}
CloseApplications=yes
RestartIfNeededByRun=no
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription={#MyAppDescription}
VersionInfoCompany={#MyAppPublisher}
VersionInfoProductName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "{cm:CreateDesktopIcon}";    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenufolder"; Description: "Create a Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE";               DestDir: "{app}"; Flags: ignoreversion
Source: "README.md";             DestDir: "{app}"; Flags: ignoreversion
Source: "cbom.ico";              DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}";               Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\cbom.ico"; Tasks: startmenufolder
Name: "{group}\Uninstall {#MyAppName}";     Filename: "{uninstallexe}";        Tasks: startmenufolder
Name: "{autodesktop}\{#MyAppName}";         Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\cbom.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\config.json"
