import json

import requests



def login_to_sana(server):
    data = {
        'username': server.server_user,
        'password': server.server_password,
    }

    response = requests.post(url=server.url_make + '/login', data=data)
    if response.status_code == 200:
        return  response, True
    else:
        return response.status_code ,False


def get_all_inbounds(server):
    headers = {
        'Accept': 'application/json',
    }
    response = requests.get(server.url_make + '/panel/api/inbounds/list', headers=headers, cookies=server.cookie_set)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def get_inbounds(server, inbound_id):
    headers = {
        'Accept': 'application/json',
    }
    response = requests.get(server.url_make + '/panel/api/inbounds/get/' + inbound_id, headers=headers, cookies=server.cookie_set)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def get_client(server, client):
    headers = {
        'Accept': 'application/json',
    }
    response = requests.get(server.url_make + "/panel/api/inbounds/getClientTraffics/" + client.email, headers=headers, cookies=server.cookie_set)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code
    
def get_clientByid(server, uuid):
    headers = {
        'Accept': 'application/json',
    }
    response = requests.get(server.url_make + "/panel/api/inbounds/getClientTrafficsById/" + uuid , headers=headers, cookies=server.cookie_set)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def get_client_ips(server, tel_id):
    headers = {
        'Accept': 'application/json',
    }
    response = requests.post(server.url_make + 'panel/api/inbounds/clientIps/' + tel_id, headers=headers, cookies=server.cookie_set)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def add_inbound(server, inbound, client):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    settings = {"clients": [
        {
            "id": str(client.uuid),
            "alterId": 0,
            "email": client.email,
            "limitIp": client.limitIp, "totalGB": client.totalGB,
            "expiryTime": client.expiryTime.timestamp() * 1000,
            "enable": True, "tgId": "", "subId": ""}
    ],"decryption":"none", "fallbacks":[]
    }

    data = {"enable": inbound.enable,
            "remark": inbound.remark,
            "listen": inbound.listen,
            "port": inbound.port,
            "protocol": "vless",
            "expiryTime": 0,
            "settings":json.dumps(settings),
            "streamSettings": "{\"network\":\"ws\",\"security\":\"none\",\"wsSettings\":{\"acceptProxyProtocol\":false,\"path\":\"\",\"headers\":{}}}",
            "sniffing": "{\"enabled\":true,\"destOverride\":[\"http\",\"tls\"]}"
            }
    response = requests.post(
        server.url_make + '/panel/api/inbounds/add',
        headers=headers,
        data=data,
        cookies=server.cookie_set
    )
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def add_client_to_inbound(server, inbound_id, client):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    settings={"clients":[
                {
                    "id":str(client.uuid),
                    "alterId":0,
                    "email":client.email,
                    "limitIp":client.limitIp,"totalGB":client.totalGB,
                     "expiryTime":client.expiryTime.timestamp() * 1000,
                    "enable":True,"tgId":"","subId":""}
    ]
    }
    data = {"id": inbound_id,
            "settings": json.dumps(settings)
            }
    response = requests.post(server.url_make + '/panel/api/inbounds/addClient', headers=headers, data=data, cookies=server.cookie_set)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def update_inbound(server, inbound, client):

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    clients = [{
        "id": client.uuid,
        "alterId": client.alter_id, "email": client.email, "limitIp": client.limitIp,
        "totalGB": client.totalGB, "expiryTime": client.expiryTime,
        "enable": client.enable, "tgId": client.tagId, "subId": client.subId}]
    data = {"enable": inbound.enable,
            "remark": inbound.remark,
            "listen": inbound.listen,
            "port": inbound.port,
            "protocol": inbound.protocol,
            "expiryTime": inbound.expiryTime,
            "settings": {"clients": clients, "decryption": "none", "fallbacks": []},
            "streamSettings": {"network": "ws", "security": "none",
                               "wsSettings": {"acceptProxyProtocol": False, "path": "", "headers": {}}},
            "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}}

    response = requests.post(server.url_make + '/panel/api/inbounds/update/' + inbound.id, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def update_client(server, inbound_id, client):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    settings = {"clients": [
        {
            "id": str(client.uuid),
            "alterId": 0,
            "email": client.email,
            "limitIp": client.limitIp, "totalGB": client.totalGB,
            "expiryTime": client.expiryTime.timestamp() * 1000,
            "enable": True, "tgId": "", "subId": ""}
    ]
    }
    data = {"id": inbound_id,
            "settings": json.dumps(settings)
            }
    response = requests.post(
        server.url_make + '/panel/api/inbounds/updateClient/' + str(client.uuid),
        headers=headers,
        data=data,
        cookies=server.cookie_set
    )
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def clear_client_ips(server, client):
    headers = {
        'Accept': 'application/json',
    }

    response = requests.post(server.url_make + '/panel/api/inbounds/clearClientIps/' + client.email, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def clear_all_inbounds(server):
    headers = {
        'Accept': 'application/json',
    }

    response = requests.post(server.url_make + '/panel/api/inbounds/resetAllTraffics', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def reset_inbounds_clients_stat(server, inbound_id):
    headers = {
        'Accept': 'application/json',
    }

    response = requests.post(server.url_make + '/panel/api/inbounds/resetAllClientTraffics/' + inbound_id, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def reset_clients_stat(server, inbound_id, client):
    headers = {
        'Accept': 'application/json',
    }

    response = requests.post(
        server.url_make + f'/panel/api/inbounds/{inbound_id}/resetClientTraffic/' + client.email,
        headers=headers,
        cookies=server.cookie_set
    )
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def delete_inbound(server, inbound_id):
    headers = {
        'Accept': 'application/json',
    }

    response = requests.post(server.url_make + '/panel/api/inbounds/del/' + inbound_id, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def delete_client(server, client):
    headers = {
        'Accept': 'application/json',
    }

    response = requests.post(
        server.url_make + f'/panel/api/inbounds/{client.inbound.inbound_id_in_server}/delClient/{client.uuid}',
        headers=headers,cookies=server.cookie_set
    )
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def delete_depleted_clients(server, inbound_id):
    headers = {
        'Accept': 'application/json',
    }

    response = requests.post(server.url_make + '/panel/api/inbounds/delDepletedClients/' + inbound_id, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def online_clients(server):
    response = requests.post(server.url_make + '/panel/api/inbounds/onlines')
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def create_backup(server):
    response = requests.get(server.url_make + '/panel/api/inbounds/createbackup')
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code
