import sys
import os
from peewee import *
from models.models import *

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from local_setting import HOST, PASSWORD, DB, USER, PORT

db = MySQLDatabase(database=DB, user=USER, password=PASSWORD, host=HOST, port=PORT)
def create_tables():
    db.create_tables([User, Server, Subscription, Transaction, Inbound, Client, ErrorLog])


def drop_tables():
    db.drop_tables([User, Server, Subscription, Transaction, Inbound, Client, ErrorLog])





