$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

$eventIdsToMonitor = @(
    5136, # Directory Service Changes
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

Get-WinEvent -FilterHashTable @{
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
        # Diagnostic output - uncomment to see in console
        #XML = $_.ToXml()
    }
} | Export-Csv -Path "<Path to save CSV>" -NoTypeInformation