
from cx_Freeze import setup, Executable
import sys, os, scipy
from os.path import dirname
base=None

os.environ['TCL_LIBRARY'] = r'C:\Users\user\Desktop\tcl8.6.6\win\Release_VC13'
os.environ['TK_LIBRARY'] = r'C:\Users\user\Desktop\tk8.6.6\win\Release_VC13'
path_platforms = ("C:\\Users\\user\\Anaconda3\\Lib\\site-packages\\PyQt5\\plugins\\platforms\\qwindows.dll", "platforms\\qwindows.dll" )
file = ('C:\\Users\\user\\Anaconda3\\Lib\\site-packages\\PyQt5\\uic\\port_v2\\invoke.py', "platforms\\invoke.py")
build_exe_options = {"packages": ["os", "numpy", 'pandas', 'PyQt5'], "includes": ["numpy", 'pandas', 'PyQt5'], "include_files": [dirname(scipy.__file__),  'environment.py', path_platforms]}

if sys.platform=='win32':
    base='Win32GUI'
setup(
    name = "Sirius",
    version = "1.0",
    description = "sadovoye ring simulator",
    options={"build_exe": build_exe_options},
    executables = [Executable('C:\\Users\\user\\Desktop\\Autopilot_sirius-sth-else2\\Autopilot_sirius-sth-else2\\Leonid\\main_interfaced.py', base=base)]
    )