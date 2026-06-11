' 月薪猫桌宠启动器 - 双击即可启动
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' 找可用的 pythonw.exe
Dim pythonwPath
pythonwPath = ""
If objFSO.FileExists(scriptDir & "\venv2\Scripts\pythonw.exe") Then
    pythonwPath = scriptDir & "\venv2\Scripts\pythonw.exe"
ElseIf objFSO.FileExists(scriptDir & "\venv\Scripts\pythonw.exe") Then
    pythonwPath = scriptDir & "\venv\Scripts\pythonw.exe"
End If

Dim mainPath
mainPath = scriptDir & "\main_tk.py"

If pythonwPath <> "" And objFSO.FileExists(mainPath) Then
    objShell.Run """" & pythonwPath & """ """ & mainPath & """", 0, False
Else
    MsgBox "未找到运行环境，请先运行 启动.bat 安装依赖", 48, "月薪猫"
End If
