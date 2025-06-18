from datetime import datetime, timedelta
import string
from random import random, choices, choice
from wsgiref.simple_server import server_version

from models.models import *


def create_test_objects():

    servers = []
    for i in range(10):
        server = Server.create(server_name="آلمان پینگ ثابت", ip_address=f"{i}",
                               status=Server.ACTIVE)
        server.save()
        servers.append(server)

    subscriptions = []
    for i in range(10):
        start_day =datetime.now()
        subscription = Subscription(
            plan=choices(string.ascii_lowercase, k=10), amount=i, status=Subscription.ACTIVE, start_date=start_day,
            end_date=start_day + timedelta(days=i)
        )
        subscription.server = servers[i].id
        subscription.user = 1
        subscription.save()
        subscriptions.append(subscription)


def create_fake_payment():
    for i in range(10):
        transaction = Transaction(user=1, amount=i*10000, status=Transaction.PLUS_CHARGE)
        transaction.save()

    for i in range(5):
        transaction = Transaction(user=1, amount=i*10000, status=Transaction.MINES_CHARGE)
        transaction.save()


def create_server():
    server = Server.create(server_address="193.36.85.198",
                           server_port="3246",
                           server_user="mmdb1376",
                           server_password="mmdbmmdb13761997",
                           location="Germany",
                           status=Server.ACTIVE,
                           server_web_pass="1Vse600BKN"
                           )
    server.save()

def creat_subscription():
    subscription = Subscription.create(
        plan="یک ماه", amount=50000, status=Subscription.ACTIVE, start_date=datetime.now(),
        total_days=30, server=1, totalGb=40000000000
    )


if __name__ == "__main__":
    create_server()
    creat_subscription()
