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
    query = "?conditions=firstName like '%" + name + "%' OR lastName like '%" + name + "%'"
    request_text = cw_url + "/company/contacts" + query
    r = get(request_text, headers=auth_header)
    data = loads(r.text)
    return data

@app.route('/<name>')
def hello_world(name):
    return_data = {}
    return_data["type"] = "message"
    return_string = None

    contacts = get_contacts(name)

    for contact in contacts:
        return_line = ""
        first = None
        last = None

        if "firstName" in contact.keys():
            first = contact["firstName"]

        if "lastName" in contact.keys():
            last = contact["lastName"]

        if first:
            return_line = first
        if last:
            if first:
                return_line = return_line + " " + last
            else:
                return_line = last

        if "communicationItems" in contact.keys():
            comm_string = None
            for comm_item in contact["communicationItems"]:
                if not comm_string:
                    comm_string = comm_item["type"]["name"] + ": " + comm_item["value"]
                else:
                    comm_string = comm_string + ", " + comm_item["type"]["name"] + " " + comm_item["value"]

            if comm_string:
                return_line = return_line + " - " + comm_string

        if not return_string:
            return_string = return_line
        else:
            return_string = return_string + "\n" + return_line

    return_data["text"] = return_string

    return dumps(return_data)