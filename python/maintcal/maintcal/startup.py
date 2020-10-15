from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig
INIFILE="/home/core/core-config/maintcal.ini"
fileConfig(INIFILE)
app = loadapp("config:%s"%INIFILE)
