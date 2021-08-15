import sys

import os

INTERP = os.path.expanduser("/var/www/u0000005/data/flaskenv/bin/python") # ПОМЕНЯТЬ ЗНАЧЕНИЯ!!! u0000005 на логинг нашей услуги хостинга, flaskenv — название вашего виртуального окружения, которое вы создали в пункте 6

# Заного пройти курс запуска сайта
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from run import application