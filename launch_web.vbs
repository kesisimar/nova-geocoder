' launch_web.vbs
' Run run_web.bat from script directory, hidden
Option Explicit
Dim fso, shell, scriptPath, scriptDir, cmd
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
scriptPath = WScript.ScriptFullName
scriptDir = fso.GetParentFolderName(scriptPath)
shell.CurrentDirectory = scriptDir
cmd = scriptDir & "\\run_web.bat"
' 0 = hidden, False = don't wait
shell.Run chr(34) & cmd & chr(34), 0, False
