from json import dumps, loads
from requests import get
from flask import Flask

app = Flask(__name__)

with open("/home/christian/secrets/cw.token") as file:
    api_key = file.read().replace("\n", "")

with open("/home/christian/secrets/cw.clientid") as file:
    client_id = file.read().replace("\n", "")

auth_header = {
    "Authorization": "Basic " + api_key,
    "Content-Type": "application/json",
    "clientid": client_id,
}

cw_url = "https://api-na.myconnectwise.net/v4_6_release/apis/3.0"


def execute_query(path, query, page=1, data=[]):
    #print("processing page %s" % page)
    request_text = cw_url + path + query + "&pagesize=1000&page=" + str(page)
    r = get(request_text, headers=auth_header)
    current_page = loads(r.text)
    #print("current page: %s" % str(current_page)[:128])
    if current_page == [] and page != 1:
        #print("we are done")
        return data
    #for company in current_page:
        #print(company["name"])
    data = data + current_page

    return execute_query(path, query, page + 1, data)


def get_contacts(contact_name):
    return execute_query(
        "/company/contacts",
        "?conditions=firstName like '%"
        + contact_name
        + "%' OR lastName like '%"
        + contact_name
        + "%'",
    )


def get_computers(client_id):
    return execute_query(
        "/company/configurations", "?conditions=type/name like 'Managed Workstation' AND status/name NOT LIKE '\%Inactive' AND company/id=" + str(client_id)
    )


def get_companies():
    return execute_query("/company/companies", "?conditions=status/name='Active'")


@app.route("/")
def index():
    companies = get_companies()
    print(len(companies))

    string = ""

    for company in companies:
        string = string + str(company["id"]) + " " + company["name"] + ": " + str(len(get_computers(company["id"]))) + "<br>\n"
        print(string)
    return string


@app.route("/api/<name>")
def api_contacts(name):
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
                    comm_string = (
                        comm_string
                        + ", "
                        + comm_item["type"]["name"]
                        + " "
                        + comm_item["value"]
                    )

            if comm_string:
                return_line = return_line + " - " + comm_string

        if not return_string:
            return_string = return_line
        else:
            return_string = return_string + "\n" + return_line

    return_data["text"] = return_string

    return dumps(return_data)
