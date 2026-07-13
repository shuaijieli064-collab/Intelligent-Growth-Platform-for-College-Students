; Inno Setup installer for 大学生智能成长平台
; 编译方法：右键此文件 → Compile（需安装 Inno Setup）

[Setup]
AppName=大学生智能成长平台
AppVersion=1.0.0
Publisher=TrainingProject
DefaultDirName={autopf}\TrainingProject
DefaultGroupName=大学生智能成长平台
OutputDir=.\output
OutputBaseFilename=TrainingPlatform_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\TrainingProject.exe
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedbydefault
Name: "quicklaunchicon"; Description: "创建快速启动栏图标"; GroupDescription: "快捷方式："; Flags: unchecked

[Files]
Source: "..\dist\TrainingProject.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\config.example.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\sql\*.sql"; DestDir: "{app}\sql"; Flags: ignoreversion
Source: "..\start_mysql.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\start_mysql.ps1"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\大学生智能成长平台"; Filename: "{app}\TrainingProject.exe"; WorkingDir: "{app}"; Comment: "大学生智能成长平台"
Name: "{group}\启动 MySQL"; Filename: "{app}\start_mysql.bat"; WorkingDir: "{app}"
Name: "{commondesktop}\大学生智能成长平台"; Filename: "{app}\TrainingProject.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\TrainingProject.exe"; Description: "启动大学生智能成长平台"; Flags: nowait postinstall skipifsilent unchecked; WorkingDir: "{app}"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('安装完成！' + #13#10 + #13#10 +
           '首次使用请按以下步骤操作：' + #13#10 +
           '1. 确保 MySQL 8.4 已安装并运行' + #13#10 +
           '2. 双击桌面快捷方式启动程序' + #13#10 +
           '3. 首次启动自动弹出配置向导，输入数据库信息' + #13#10 +
           '4. 点击「测试连接并初始化数据库」完成初始化', 
           mbInformation, MB_OK);
  end;
end;
