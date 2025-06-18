
from datetime import datetime, timedelta
import uuid
import random

import requests
import segno
from idna.intranges import intranges_from_list
from peewee import Model, DateTimeField, CharField, IntegerField, ForeignKeyField, SmallIntegerField, fn, BooleanField, \
    DecimalField, BigIntegerField, FloatField
from pyexpat.errors import messages
from pymysql.constants.ER import USER_LIMIT_REACHED

from Api.sanaii_api import add_inbound, add_client_to_inbound, delete_client, get_client, update_client, \
    reset_clients_stat, get_all_inbounds, get_clientByid
from db_config import db


class BaseModel(Model):
    created_time = DateTimeField(default=datetime.now)
    modify_time = DateTimeField(default=datetime.now)

    class Meta:
        database = db


class ErrorLog(BaseModel):
    message = CharField(null=True)
    location = CharField(null=True)

    class Meta:
        database = db
        table_name = 'logs'

    @staticmethod
    def decorate_method_for_error(func):
        def wrapper_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorLog(message=e, location=str(func)).create()
                return False, e, None

        return wrapper_func






class User(BaseModel):
    SUPER_ADMIN = 0
    ADMIN = 1
    NORMAL = 2

    USER_ROLES = ((SUPER_ADMIN, "SUPER_ADMIN"),
                  (ADMIN, "ADMIN"),
                  (NORMAL, "NORMAL"))

    username = CharField(unique=True)
    password = CharField()
    email = CharField(null=True)
    tel_id = IntegerField(unique=True)
    role = SmallIntegerField(choices=USER_ROLES, default=NORMAL)

    class Meta:
        database = db
        table_name = 'users'

    @property
    def inventory(self):
        inventory_value_plus = (User.select(fn.SUM(Transaction.amount).alias('amount'))
                                .where(User.id == self.id)
                                .join(Transaction, on=(Transaction.user == User.id))
                                .where(Transaction.status == Transaction.PLUS_CHARGE))

        inventory_value_mines = (User.select(fn.SUM(Transaction.amount).alias('amount'))
                                 .where(User.id == self.id)
                                 .join(Transaction, on=(Transaction.user == User.id))
                                 .where(Transaction.status == Transaction.MINES_CHARGE))

        return (inventory_value_plus[0].amount or 0) - (inventory_value_mines[0].amount or 0)

    def make_role(self, role):
        if role is int and role < 3:
            self.role = self.USER_ROLES[role]
            return "role changed"
        else:
            "it is not a stable value"

    @classmethod
    @ErrorLog.decorate_method_for_error
    def show_clients_for_userid(cls, userid):
        query = User.select().where(User.tel_id==userid)
        return query[0]


class Server(BaseModel):
    ACTIVE = 1
    DISABLE = 2
    SERVER_STATUS = ((ACTIVE, "ACTIVE"), (DISABLE, "DISABLE"))
    server_address = CharField(unique=True)
    server_port = CharField(unique=True)
    server_user = CharField(unique=True)
    server_password = CharField(unique=True)
    server_web_pass = CharField(null=True)
    location = CharField(null=True)
    status = SmallIntegerField(choices=SERVER_STATUS, default=DISABLE)

    @property
    @ErrorLog.decorate_method_for_error
    def cookie_set(self):
        try:
            data = {
                'username': self.server_user,
                'password': self.server_password,
            }
            url=self.url_make
            response = requests.post(url=url + '/login', data=data)
            if response.status_code == 200:
                cookie = response.cookies
                return cookie
            else:
                return None
        except :
            return None

    @property
    @ErrorLog.decorate_method_for_error
    def url_make(self):
        return f"https://{self.server_address}:{self.server_port}/{self.server_web_pass}"

    class Meta:
        database = db
        table_name = 'servers'

    def __str__(self):
        return str(self.location + " " + str(self.id))

    @classmethod
    @ErrorLog.decorate_method_for_error
    def show_servers(cls):
        servers = cls.select().where(cls.status == cls.ACTIVE).execute()
        return servers
    
    @ErrorLog.decorate_method_for_error
    def get_value_user_server(self, uuid):
        api_result = get_clientByid(server=self, uuid=uuid)
        if api_result.get("success") and api_result.get("obj"):
            return api_result["obj"][0]
        else:
            return None

    

    @ErrorLog.decorate_method_for_error
    def change_server_inbound_client(self, inbound, client, server):
        inbound_ex = Inbound.get_or_none(Inbound.id==inbound.id, Inbound.server==self)
        if inbound_ex:
            clients = inbound_ex.clients
            client.uuid = uuid.uuid4()
            number_clients = len(clients)
            client.email = f"uservpn_{number_clients+1}_{client.user.tel_id}_{self.id}"
            response = add_client_to_inbound(self,inbound_ex.inbound_id_in_server, client)
            if response["success"]:
                client.inbound = inbound_ex
                client.save()
                delete_response = delete_client(server, client)
                if delete_response["success"]:
                    pass
                else:
                    pass

                return True, response["msg"], client
            else:
                return False,response["msg"], None

        else:
            client.email = f"uservpn_1_{client.user.tel_id}_{self.id}"
            response = add_inbound(self, inbound, client)
            if response["success"]:
                new_inbound = Inbound(remark=f"inbovpn_{self.id}_{client.user.tel_id}", server=self,
                              protocol=Inbound.VLESS)
                new_inbound.port = new_inbound.make_random_port()
                client.inbound=new_inbound.save()

                client.save()
                delete_response = delete_client(server, client)
                if delete_response["success"]:
                    pass
                else:
                    pass
                return True, response["msg"], client
            else:
                return False,response["msg"], None


class Subscription(BaseModel):
    ACTIVE = 1
    DISABLE = 2

    SUBSCRIPTION_STATUS = ((ACTIVE, "ACTIVE"),
                           (DISABLE, "DISABLE"))

    plan = CharField()
    amount = IntegerField(default=0)
    server = ForeignKeyField(Server, backref='subscriptions')
    total_days= FloatField(default=0)
    totalGb = BigIntegerField(default=0)
    status = SmallIntegerField(choices=SUBSCRIPTION_STATUS, default=ACTIVE)

    class Meta:
        database = db
        table_name = 'subscriptions'

    @classmethod
    @ErrorLog.decorate_method_for_error
    def show_subscriptions_by_server_id(cls, server_id):
        subscriptions = cls.select().where(cls.status == Subscription.ACTIVE).where(cls.server == server_id)
        return subscriptions




class Inbound(BaseModel):
    class Meta:
        database = db
        table_name = 'inbounds'

    TROJAN = 0
    VLESS = 1
    VMSS = 2
    PROTOCOL_VALUES = (
        (TROJAN, "trojan"),
        (VLESS, "vless"),
        (VMSS, "vmss")
    )
    enable = BooleanField(default=True)
    remark = CharField(null=True)
    listen = CharField(null=True)
    port = IntegerField(unique=True)
    protocol = SmallIntegerField(choices=PROTOCOL_VALUES, default=VLESS)
    inbound_id_in_server = IntegerField(default=0)
    expiryTime = DateTimeField(null=True)
    server = ForeignKeyField(Server, on_delete="CASCADE", related_name="inbounds")

    def __str__(self):
        return self.remark

    def make_random_port(self):
        num = random.randint(1000, 99999)
        if Inbound.get_or_none(Inbound.port==num) or Server.get_or_none(Server.server_port==num):
            self.make_random_port()
        else:
            return num


class Client(BaseModel):
    class Meta:
        database = db
        table_name = 'clients'

    uuid = CharField(unique=True)
    alter_id = CharField(null=True)
    email = CharField(unique=True)
    limitIp = IntegerField(default=1)
    totalGB = BigIntegerField(default=0)
    expiryTime = DateTimeField()
    enable = BooleanField(default=True)
    tagId = CharField(null=True)
    subId = CharField(null=True)
    inbound = ForeignKeyField(Inbound, on_delete='CASCADE', related_name='clients')
    user = ForeignKeyField(User, on_delete="CASCADE", related_name="clients")
    subscription = ForeignKeyField(Subscription, on_delete="CASCADE", related_name="clients")

    def save(self, force_insert = ..., only = ...):
        self.uuid = uuid.uuid4()
        super().save()


    def make_config(self):
        inbound = self.inbound
        server = inbound.server
        if self.inbound.protocol == Inbound.VLESS:
            vless_link = (f"vless://{self.uuid}@{server.server_address}"
                          f":{server.server_port}?type=tcp&security=none#{inbound.remark}-{self.email}")
            return vless_link
        else:
            return None

    @ErrorLog.decorate_method_for_error
    def get_url_qrcode(self):
        url = self.make_config()
        img = segno.make_qr(url)
        return url, img.save("basic_qrcode.png", scale=10)

    @ErrorLog.decorate_method_for_error
    def extension_client(self):
            inbound = self.inbound
            server =inbound.server
            subscription =self.subscription
            client_api = get_client(server, self)
            self.expiryTime= datetime.now() + timedelta(days=subscription.total_days)
            response = update_client(server,  inbound.inbound_id_in_server, self)
            if response["success"]:
                response = reset_clients_stat(server,  inbound.inbound_id_in_server, self)
                if response["success"]:
                    self.save()
                    return  True, response["msg"]
            else:
                return False,response["msg"]

    @classmethod
    @ErrorLog.decorate_method_for_error
    def create_inbound_client(cls, subscription, user):
        server = subscription.server
        inbound = Inbound.get_or_none(Inbound.enable == True, Inbound.remark == f"inbovpn_{server.id}_{user.tel_id}",
                                      server=server)
        if inbound is None:
            inbound = Inbound(remark=f"inbovpn_{server.id}_{user.tel_id}", server=server,
                              protocol=Inbound.VLESS
                              )
            inbound.port = inbound.make_random_port()
            client = Client(email=f"uservpn_1_{user.tel_id}_{server.id}", limitIp=1, totalGB=subscription.totalGb,
                            expiryTime=datetime.now() + timedelta(days=subscription.total_days), inbound=inbound,
                            user=user, subscription=subscription)
            response = add_inbound(server=server, inbound=inbound, client=client)
            if response["success"]:
                inbound.inbound_id_in_server = response["obj"]["id"]
                inbound.save()
                client.save()
                return True, response["msg"], client

            else:
                return False, response["msg"], None

        else:
            clients = inbound.clients
            number_clients = len(clients)
            client = Client(email=f"uservpn_{number_clients + 1}_{user.tel_id}_{server.id}", limitIp=1,
                            totalGB=subscription.totalGb,
                            expiryTime=datetime.now() + timedelta(days=subscription.total_days), inbound=inbound,
                            user=user, subscription=subscription)

            response = add_client_to_inbound(server, inbound.inbound_id_in_server, client)
            if response["success"]:
                client.save()
                return True, response["msg"], client

            else:
                return False, response["msg"], None




class Transaction(BaseModel):
    SUCCESSFUL_PAYMENT = 1
    PLUS_CHARGE = 2
    MINES_CHARGE = 3
    FAILED_PAYMENT = 0

    PAYMENT_CHOICES = ((SUCCESSFUL_PAYMENT, 'Successful payment'), (FAILED_PAYMENT, 'Failed payment')
                       , (PLUS_CHARGE, 'charge payment'), (MINES_CHARGE, 'buy config '))

    user = ForeignKeyField(User, backref='payments')
    amount = IntegerField()
    status = SmallIntegerField(choices=PAYMENT_CHOICES, default=FAILED_PAYMENT)

    class Meta:
        database = db
        table_name = 'transactions'

