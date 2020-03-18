if( $args.Count -lt 1 ){
	Write-Host "Usage: acl_check.ps1 <Path>"
	Exit(1)
}

$test_file_path = $args[0]
$users = "Users","Everyone","Authenticated Users"


Get-ChildItem $test_file_path -Recurse -ErrorAction SilentlyContinue | %{ 
	
	try {
		$file_path = $_.FullName
		Get-Acl $file_path -ErrorAction SilentlyContinue | 
		%{ 
			$perm_list = New-Object System.Collections.ArrayList($null)
			$_.Access | 
			%{
				foreach( $user in $users ){
					$user_account = ([string]$_.IdentityReference)
					$rights = ([string]$_.FileSystemRights)
					if( $user_account -like "*" + $user + "*" ){	
						if($rights -like "*Write*" -or $rights -like "*Create*"){
							$null = $perm_list.Add( $user_account + "`n" + $rights )
						}
					}
				}
			}
			
			if( $perm_list.Count -gt 0 ){
				Write-Host "`nPath: $file_path"
				$perm_list | 
				%{
					Write-Host $_
				}
			}
		} 
		
	} catch [Exception]{
		echo $_.Exception.GetType().FullName, $_.Exception.Message
	}
}
