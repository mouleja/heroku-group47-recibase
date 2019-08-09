from app import app
from flaskext.mysql import MySQL

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'wnxexw4d5gzwq8vz'
app.config['MYSQL_DATABASE_PASSWORD'] = 'vxiynmz8cej3riyg'
app.config['MYSQL_DATABASE_DB'] = 'osgcsiit2szj8f48'
app.config['MYSQL_DATABASE_HOST'] = 'c584md9egjnm02sk.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
mysql.init_app(app)
