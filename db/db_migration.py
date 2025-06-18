from db.db_config import db
from models.models import User, Server, Subscription, Transaction, Inbound, Client, ErrorLog


def create_tables():
    db.create_tables([User, Server, Subscription, Transaction, Inbound, Client, ErrorLog])


def drop_tables():
    db.drop_tables([User, Server, Subscription, Transaction, Inbound, Client, ErrorLog])


if __name__ == '__main__':
    drop_tables()
    create_tables()
