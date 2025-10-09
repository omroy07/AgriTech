@echo off 
echo Adding viewport meta tag to all HTML files... 
 
for %%f in (*.html) do ( 
  echo Processing %%f 
  copy "%%f" "%%f.bak" 
  powershell -Command "$content = Get-Content '%%f' -Raw; $content = $content -replace '<head>', '<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">'; $content | Out-File -Encoding UTF8 '%%f'" 
) 
 
echo Viewport tags added successfully! 
pause 
