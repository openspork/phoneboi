from .helpers import *


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
        query="?conditions=product/identifier='%s' AND cancelledDate=null"
        % product_identifier,
    )


def process_products(agreement_name, product_identifier, configuration_type):
    companies = []

    for agreement in get_agreements(agreement_name):
        print("Processing %s: %s" % (agreement["company"]["name"], agreement["name"]))

        company = {}
        company["name"] = agreement["company"]["name"]
        company["configurations"] = len(
            get_configurations(
                company_id=agreement["company"]["id"],
                configuration_type=configuration_type,
            )
        )

        products = get_products(
            agreement_id=agreement["id"], product_identifier=product_identifier
        )

        company["products"] = len(products)

        quantity_sum = 0
        for product in products:
            quantity_sum = quantity_sum + product["billedQuantity"]

        company["product_sum"] = quantity_sum

        companies.append(company)
    return companies
