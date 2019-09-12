from .helpers import *
from uuid import uuid4
from operator import itemgetter

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
        path="/finance/agreements", query="?conditions=type/name LIKE '%s' AND agreementStatus='Active'" % agreement_type
    )


def get_products(agreement_id, product_identifier):
    return execute_query(
        path="/finance/agreements/%s/additions" % agreement_id,
        query="?conditions=product/identifier LIKE '%s' AND cancelledDate=null"
        % product_identifier,
    )


def process_products(agreement_name, product_identifier, configuration_type):
    companies = {}

    for agreement in get_agreements(agreement_name):
        print("Processing %s: %s" % (agreement["company"]["name"], agreement["name"]))

        company = {}
        company["company_name"] = agreement["company"]["name"]
        company["configuration_count"] = len(
            get_configurations(
                company_id=agreement["company"]["id"],
                configuration_type=configuration_type,
            )
        )



        products = get_products(
            agreement_id=agreement["id"], product_identifier=product_identifier
        )

        company["product_count"] = len(products)

        product_sum = 0
        billed_sum = 0
        less_sum = 0
        
        for product in products:
            product_sum = product_sum + product["quantity"]
            billed_sum = billed_sum + product["billedQuantity"]
            less_sum = less_sum + product["lessIncluded"]

        company["product_sum"] = product_sum
        company["billed_sum"] = billed_sum
        company["configuration_count_adj"] = company["configuration_count"] - less_sum

        companies[uuid4()] = company
    return sorted(companies, key=itemgetter("company_name")) 


def init_products():
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
    return products