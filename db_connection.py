from app import app
from flaskext.mysql import MySQL

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'cs340_mouleja'
app.config['MYSQL_DATABASE_PASSWORD'] = '6778'
app.config['MYSQL_DATABASE_DB'] = 'cs340_mouleja'
app.config['MYSQL_DATABASE_HOST'] = 'classmysql.engr.oregonstate.edu'
mysql.init_app(app)
