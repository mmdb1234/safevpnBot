import sys
import os
from peewee import *
import pymysql

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from local_setting import HOST, PASSWORD, DB, USER, PORT

db = MySQLDatabase(database=DB, user=USER, password=PASSWORD, host=HOST, port=PORT)






