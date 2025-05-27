$disk = Get-PSDrive C
if (($disk.Free / $disk.Total) -lt 0.1) {
    $body = @{title="Low disk space on C:"} | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:5000/api/incidents" -Method Post -Body $body -ContentType "application/json"
}