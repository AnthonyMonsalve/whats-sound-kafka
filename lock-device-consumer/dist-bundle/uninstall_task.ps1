param([string]$TaskName = "PC Lock Consumer")
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "OK: Tarea eliminada."
}
