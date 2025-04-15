$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

$eventIdsToMonitor = @(
    4728, # A member was added to a security-enabled global group
    4729, # A member was removed from a security-enabled global group
    4732, # A member was added to a security-enabled local group
    4733, # A member was removed from a security-enabled local group
    4741, # A computer account was created
    4742, # A computer account was changed
    4743, # A computer account was deleted
    4720, # A user account was created
    4722, # A user account was enabled
    4723, # An attempt was made to change an account's password
    4724, # An attempt was made to reset an account's password
    4725, # A user account was disabled
    4726, # A user account was deleted
    4738, # A user account was changed
    4756, # A security-enabled universal group was created
    4757, # A member was added to a security-enabled universal group
    4758, # A member was removed from a security-enabled universal group
    4763  # Universal Group Membership changes
    # Add other relevant Event IDs here for group membership changes
)

# Check if script is running with elevated privileges
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
{
    Write-Host "This script requires elevated privileges. Please run as Administrator."
    $arguments = "-File `"$PSCommandpath`""
    Start-Process PowerShell -Verb RunAs -ArgumentList $arguments
    exit 
}

# Specify the name of the remote domain controller
$remoteDC = "Remote computer" # Replace with the actual FQDN or NetBIOS name

# Function to gather events from a computer
function Get-ADLogEvents {
    param(
        [string]$ComputerName
    )
    Write-Host "Gathering logs from: $ComputerName"
    Get-WinEvent -ComputerName $ComputerName -FilterHashTable @{
        LogName = 'Security'
        Id = $eventIdsToMonitor
        StartTime = $startDate
        EndTime = $endDate
    } | ForEach-Object {
        $recordData = [xml]$_.ToXml()
        $eventData = $recordData.Event.EventData

        $subjectAccount = if ($eventData.SubjectUserName) {$eventData.SubjectUserName.'#text'} else {$null}
        $memberSecurityID = if ($eventData.MemberSid) {$eventData.MemberSid.'#text'} else {$null}
        $memberAccountName = if ($eventData.MemberName) {$eventData.MemberName.'#text'} else {$null}
        $groupName = if ($eventData.TargetUserName) {$eventData.TargetUserName.'#text'} else {$null}

        [PSCustomObject]@{
            TimeCreated       = $_.TimeCreated
            EventID           = $_.Id
            Message           = $_.Message
            SubjectAccount    = $subjectAccount
            MemberSecurityID  = $memberSecurityID
            MemberAccountName = $memberAccountName
            GroupName         = $groupName
            SourceComputer    = $ComputerName # Add a column to identify the source
            # Diagnostic output - uncomment to see in console
            #XML = $_.ToXml()
        }
    }
}

# Gather events from the local computer
$localEvents = Get-ADLogEvents -ComputerName $env:COMPUTERNAME

# Gather events from the remote domain controller
$remoteEvents = Get-ADLogEvents -ComputerName $remoteDC

# Combine the events
$allEvents = $localEvents + $remoteEvents

# Export the combined events to a CSV file
$allEvents | Export-Csv -Path "<path to export csv>" -NoTypeInformation

Write-Host "Logs gathered from local computer and '$remoteDC' and exported to CSV"