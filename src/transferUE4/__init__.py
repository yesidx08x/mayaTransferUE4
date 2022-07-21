#!/usr/bin/python
#coding=utf-8
import os
import main
reload(main)
import exportFbx
reload(exportFbx)
print(os.path.dirname(__file__) + "/uassetConvert.py")
mainWin = main.mainWin
currentPath = r"E:/work_ref/transferUE4/transferUE4"
uiPath = os.path.join(currentPath, "transferUE4.ui")
subUiPath = os.path.join(currentPath, "checkFiles.ui")
uepyfile = os.path.dirname(__file__) + "/uassetConvert.py"