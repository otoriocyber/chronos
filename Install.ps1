$get_zimmerman_tools_urls = 'https://f001.backblazeb2.com/file/EricZimmermanTools/Get-ZimmermanTools.zip'
$flare_wmi_url = 'https://github.com/fireeye/flare-wmi/archive/master.zip'
$fireeye_bits_parser = 'https://github.com/fireeye/BitsParser/archive/refs/heads/master.zip'
$browsinghistoryview_url = 'https://www.nirsoft.net/utils/browsinghistoryview-x64.zip'
$evtx_dump_url = 'https://github.com/omerbenamram/evtx/releases/download/v0.6.9/evtx_dump-v0.6.9-x86_64-pc-windows-msvc.tar.gz'
$ese_analyst_url = "https://github.com/MarkBaggett/ese-analyst/archive/master.zip"

$home_direcory = $pwd

python -m pip install -r requirements.txt

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host "Downloading Eric tools"
(New-Object Net.WebClient).DownloadFile($get_zimmerman_tools_urls, "$home_direcory/Get-ZimmermanTools.zip")
Expand-Archive -Path 'Get-ZimmermanTools.zip' -DestinationPath . -Force
Remove-Item $pwd\Get-ZimmermanTools.zip

.\Get-ZimmermanTools.ps1 -Dest Tools
Remove-Item $pwd\Get-ZimmermanTools.ps1
Set-Location Tools

Write-Host "Downloading flare wmi"
(New-Object Net.WebClient).DownloadFile($flare_wmi_url , "$pwd/flare-wmi.zip")
Expand-Archive -Path 'flare-wmi.zip' -DestinationPath . -Force
Remove-Item $pwd\flare-wmi.zip

Write-Host "Downloading BitsParser"
(New-Object Net.WebClient).DownloadFile($fireeye_bits_parser , "$pwd/bits_parser.zip")
Expand-Archive -Path 'bits_parser.zip' -DestinationPath . -Force
Remove-Item $pwd\bits_parser.zip

Write-Host "Downloading Browsing history"
(New-Object Net.WebClient).DownloadFile($browsinghistoryview_url, "$pwd/browsinghistoryview-x64.zip")
Expand-Archive -Path 'browsinghistoryview-x64.zip' -DestinationPath . -Force
Remove-Item $pwd\browsinghistoryview-x64.zip
Remove-Item $pwd\BrowsingHistoryView.chm
Remove-Item $pwd\readme.txt

Write-Host "Downloading evtx dump"
(New-Object Net.WebClient).DownloadFile($evtx_dump_url, "$pwd/evtx_dump-v0.6.9-x86_64-pc-windows-msvc.tar.gz")
tar -xvzf 'evtx_dump-v0.6.9-x86_64-pc-windows-msvc.tar.gz'
Remove-Item $pwd\evtx_dump-v0.6.9-x86_64-pc-windows-msvc.tar.gz

Write-Host "Downloading ese analyst"
(New-Object Net.WebClient).DownloadFile($ese_analyst_url , "$pwd/ese_analyst.zip")
Expand-Archive -Path 'ese_analyst.zip' -DestinationPath . -Force
Remove-Item $pwd\ese_analyst.zip


# Installing the flare wmi framework
Set-Location flare-wmi-master/python-cim/
python setup.py install

# Back to the root directory
Set-Location $home_direcory

