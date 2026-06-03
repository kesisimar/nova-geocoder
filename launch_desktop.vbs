    ' launch_desktop.vbs
    ' Run run_desktop.bat from script directory (shows console for errors)
    Option Explicit
    Dim fso, shell, scriptPath, scriptDir, cmd
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set shell = CreateObject("WScript.Shell")
    scriptPath = WScript.ScriptFullName
    scriptDir = fso.GetParentFolderName(scriptPath)
    shell.CurrentDirectory = scriptDir
    cmd = scriptDir & "\\run_desktop.bat"
    ' 1 = normal window, False = don't wait
    shell.Run chr(34) & cmd & chr(34), 1, False
