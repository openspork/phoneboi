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
        path="/finance/agreements", query="?conditions=type/name='%s'" % agreement_type
    )


def get_products(agreement_id, product_identifier):
    return execute_query(
        path="/finance/agreements/%s/additions" % agreement_id,
        query="?conditions=product/identifier='%s' AND cancelledDate=null"
        % product_identifier,
    )

# Pass a tuple of (configuration name, product identifier)
def process_products(configuration_name, product_identifier):
