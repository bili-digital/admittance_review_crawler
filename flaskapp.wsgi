import sys
sys.path.insert(0, '/var/www/html/flaskapp')
sys.path.insert(1, '/home/johnliu/flaskapp/env/lib/python3.5/site-packages')
sys.path.insert(2, '/home/johnliu/flaskapp/.env')
from main import app as application
