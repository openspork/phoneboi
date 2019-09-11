from json import dumps, loads
from requests import get
from flask import Flask, render_template
from util.process_api import *

app = Flask(__name__)


products = {}

products["phones"] = { "agreement_name":"ITSG - VOIP", "product_identifier":"VOIP - User Licenses", "configuration_type":"Managed Phone" }
products["workstations"] = { "agreement_name":"MSP%", "product_identifier":"Add Workstations%", "configuration_type":"Managed Workstation" }
products["servers"] = { "agreement_name":"MSP%", "product_identifier":"Add Servers%", "configuration_type":"Managed Server" }

for key, val in products.items():

    products[key] = process_products(
        agreement_name=val["agreement_name"],
        product_identifier=val["product_identifier"],
        configuration_type=val["configuration_type"],
    )


@app.route("/")
def index():
    return render_template("index.html", products=products)


def get_contacts(contact_name):
    return execute_query(
        "/company/contacts",
        "?conditions=firstName like '%"
        + contact_name
        + "%' OR lastName like '%"
        + contact_name
        + "%'",
    )


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
