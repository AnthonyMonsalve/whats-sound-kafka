param(
  [string]$ExePath = "C:\Users\22ant\Documents\whats-sound-kafka\lock-device-consumer\dist-bundle\pc-lock-consumer.exe",
  [string]$WorkDir = "C:\Users\22ant\Documents\whats-sound-kafka\lock-device-consumer\dist-bundle",
  [string]$TaskName = "PC Lock Consumer"
)

# Crea carpeta destino
New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null

# Acción
$action = New-ScheduledTaskAction -Execute $ExePath -WorkingDirectory $WorkDir
# Disparadores
$trLogon   = New-ScheduledTaskTrigger -AtLogOn
$trStartup = New-ScheduledTaskTrigger -AtStartup
# Config
$settings = New-ScheduledTaskSettingsSet `
  -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
  -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -ExecutionTimeLimit (New-TimeSpan -Hours 0)
# Principal: usuario actual
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Limited

# Si existe, la elimina
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($trLogon, $trStartup) -Settings $settings -Principal $principal | Out-Null
Start-ScheduledTask -TaskName $TaskName
Write-Host "OK: Tarea '$TaskName' creada y lanzada."
