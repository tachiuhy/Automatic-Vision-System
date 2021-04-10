@echo off
title Convert .ui file into .py file
set ui= Default
set py= Default
echo Enter .ui file name: 
set /p ui=
echo Enter .py file name: 
set /p py=
pyuic5 -x %ui%.ui -o %py%.py
echo Convert Successfuly!
pause
exit