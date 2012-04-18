from distutils.core import setup
import py2exe
"""console=['gui.py'], """
setup(windows=[{"script": "gui.py", 
                "icon_resources":[(0, "cal.ico")]}])