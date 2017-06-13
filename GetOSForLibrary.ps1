
if ($args.length -gt 0) {

   #Windows OS table
   $dict = @{}
   $dict.Add('5.1.2600','Windows XP')
   $dict.Add('5.2.3790','Windows Server 2003')
   $dict.Add('6.0.6000','Windows Vista')
   $dict.Add('6.0.6001','Windows Server 2008')
   $dict.Add('6.0.6002','Windows Vista SP2 or Windows Server 2008 SP2')
   $dict.Add('6.1.7600','Windows 7 or Windows Server 2008 R2')
   $dict.Add('6.1.7601','Windows 7 SP1 or Windows Server 2008 R2 SP1')
   $dict.Add('6.2.9200','Windows 8 or Windows Server 2012')
   $dict.Add('6.3.9600','Windows 8.1 or Windows Server 2012 R2')
   $dict.Add('10.0.10249','Windows 10 (2015-07-29)')
   $dict.Add('10.0.10586','Windows 10 (2015-11-12)')
   $dict.Add('10.0.14393','Windows 10 or Windows Server 2016 (2016-07-18)')
   $dict.Add('10.0.15063','Windows 10 (2017-04-11)') 

   $file_path = $args[0]
   $file_version = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($file_path).FileVersion
   $ver_arr = $file_version.split(".")
   $ver = $ver_arr[0..2] -join "."
   $win = $dict.Get_Item($ver)
   
   #If nothin returned set to unknown
   if ($win.length -eq 0){
      $win = "Unknown"
   }
   
   $file_name = [System.IO.Path]::GetFileName($file_path)
   $header = '{0,-25} {1,-30}' -f "File:", "Operating System:"
   Write-Host "`n$header"
   Write-Host "============================================"
   $str = '{0,-25} {1,-30}' -f $file_name, $win
   Write-Host $str
   
} else {
   Write-Host "Usage: .\GetOSForLibrary.ps1 <Library Path>"
}