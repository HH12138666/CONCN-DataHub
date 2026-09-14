$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Open PowerShell as Administrator and run this script again.'
}
$ruleName = 'CONCN-DataHub-LAN-TCP'
$settings = @{
    Direction = 'Inbound'
    Action = 'Allow'
    Protocol = 'TCP'
    LocalPort = 8100
    LocalAddress = @('192.168.1.38', '172.17.119.129')
    RemoteAddress = @('192.168.1.0/24', '172.17.64.0/18')
    Profile = 'Any'
    Enabled = 'True'
}
# Bind to the actual adapters, without depending on localized interface names.
$settings.InterfaceAlias = @(Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -in $settings.LocalAddress } |
    Select-Object -ExpandProperty InterfaceAlias -Unique)
if ($settings.InterfaceAlias.Count -ne 2) {
    throw 'The LAN addresses have changed. Update the addresses and subnets in this script first.'
}
if (Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue) {
    Set-NetFirewallRule -Name $ruleName @settings | Out-Null
} else {
    New-NetFirewallRule -Name $ruleName -DisplayName 'CONCN DataHub LAN 8100' @settings | Out-Null
}
Write-Output 'LAN access enabled on TCP 8100 for the two configured local subnets.'
