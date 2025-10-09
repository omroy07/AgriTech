@echo off 
echo ======================================== 
echo    AGRI TECH MOBILE RESPONSIVENESS SETUP 
echo ======================================== 
 
echo Step 1: Adding viewport tags to all HTML files... 
call fix_viewport.bat 
 
echo Step 2: Creating mobile CSS files... 
echo û mobile-base.css created 
echo û responsive.css created 
echo û mobile-main.css created 
 
echo Step 3: Creating mobile-optimized pages... 
echo û mobile-main.html created 
echo û test-mobile.html created 
 
echo ? MOBILE RESPONSIVENESS SETUP COMPLETE! 
echo. 
echo Next steps: 
echo 1. Open test-mobile.html in browser to verify responsiveness 
echo 2. Open mobile-main.html to see the new mobile layout 
echo 3. Test on actual mobile devices 
echo. 
pause 
