
from cx_Freeze import setup, Executable
import sys, os, scipy
from os.path import dirname
base=None

os.environ['TCL_LIBRARY'] = r'C:\Users\user\Desktop\tcl8.6.6\win\Release_VC13'
os.environ['TK_LIBRARY'] = r'C:\Users\user\Desktop\tk8.6.6\win\Release_VC13'

build_exe_options = {"packages": ["os", "numpy"], "includes": ["numpy"], "include_files": [dirname(scipy.__file__)]}

if sys.platform=='win32':
    base='Win32GUI'
setup(
    name = "Sirius",
    version = "1.0",
    description = "sadovoye ring simulator",
    options={"build_exe": build_exe_options},
    executables = [Executable('C:/Users/user/Desktop/old/Autopilot_sirius-master/Leonid/main.py', base=base)]
    )