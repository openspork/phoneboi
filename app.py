from json import dumps, loads
from requests import get
from flask import Flask, render_template

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
    # print("processing page %s" % page)
    request_text = "%s%s%s&pagesize=1000&page=%s" % (cw_url, path, query, page)
    # print(request_text)
    r = get(request_text, headers=auth_header)
    current_page = loads(r.text)
    # print("current page: %s" % str(current_page)[:128])
    if (current_page == [] and page != 1) or current_page == {}:
        # print("we are done")
        return data
    data = data + current_page
    return execute_query(path, query, page + 1, data)


def get_companies():
    return execute_query("/company/companies", "?conditions=status/name='Active'")


def get_configurations(company_id, configuration_type):
    return execute_query(
        path="/company/configurations",
        query="?conditions=type/name like '%s' AND status/name NOT LIKE '%%Inactive' AND company/id=%s"
        % (configuration_type, company_id),
    )


def get_agreements(agreement_type):
    return execute_query(
        path="/finance/agreements", query="?conditions=type/name='%s'" % agreement_type
    )


def get_products(agreement_id, product_identifier):
    return execute_query(
        path="/finance/agreements/%s/additions" % agreement_id,
        query="?conditions=product/identifier='%s' AND cancelledDate=null"
        % product_identifier,
    )


@app.route("/")
def index():

    companies = []

    for agreement in get_agreements("ITSG - VOIP"):
        print(agreement["name"])
        print(agreement["company"]["id"])
        print(
            len(
                get_configurations(
                    company_id=agreement["company"]["id"],
                    configuration_type="Managed Phone",
                )
            )
        )

        company = {}
        company["name"] = agreement["company"]["name"]
        company["configurations"] = len(
            get_configurations(
                company_id=agreement["company"]["id"],
                configuration_type="Managed Phone",
            )
        )

        products = get_products(
            agreement_id=agreement["id"], product_identifier="VOIP - User Licenses"
        )

        company["products"] = len(products)

        quantity_sum = 0
        for product in products:
            quantity_sum = quantity_sum + product["quantity"]

        company["product_sum"] = quantity_sum

        companies.append(company)

    return render_template("index.html", companies=companies)


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
