from json import dumps, loads
from requests import get
from flask import Flask
app = Flask(__name__)

with open('/home/christian/secrets/cw.token') as file:
    api_key = file.read().replace('\n', '')

auth_header = {"Authorization":"Basic " + api_key,
             "Content-Type":"application/json"}

cw_url = "https://api-na.myconnectwise.net/v4_6_release/apis/3.0"

def get_contacts(name):
    query = "?conditions=firstName like '" + name + "' OR lastName like '" + name + "'"
    request_text = cw_url + "/company/contacts" + query
    r = get(request_text, headers=auth_header)
    print(r.text)
    data = loads(r.text)
    return data

@app.route('/<name>')
def hello_world(name):
    hello = {}
    hello["type"] = "message"
    hello["text"] = "Hello, World!"
    contacts = get_contacts(name)

    for contact in contacts:
        print(contact["firstName"] + " " + contact["lastName"])



    return dumps(hello)
