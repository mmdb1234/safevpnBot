import json

import requests

def get_user_hidefy(server, uuid):
    headers = {
        'Accept': 'application/json',
        'Hiddify-API-Key':'105fd962-a900-44ed-944a-68f488d53493'
    }
    api = server.url_make + f'/api/v2/admin/user/{uuid}/'
    response = requests.get(api, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code