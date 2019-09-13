from uuid import uuid4
from .helpers import *
from models import *


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
        path="/finance/agreements",
        query="?conditions=type/name LIKE '%s' AND agreementStatus='Active'"
        % agreement_type,
    )


def get_additions(agreement_id, product_identifier):
    return execute_query(
        path="/finance/agreements/%s/additions" % agreement_id,
        query="?conditions=product/identifier LIKE '%s' AND cancelledDate=null"
        % product_identifier,
    )


def process_products(agreement_name, product_identifier, configuration_type):
    print(
        "processing: \n%s\n%s\n%s\n"
        % (agreement_name, product_identifier, configuration_type)
    )

    # Create configuration type, if doesn't exist
    query = ConfigurationType.select().where(
        ConfigurationType.name == configuration_type
    )

    if not query.exists():
        print("config type create: %s" % configuration_type)
        configuration_type = ConfigurationType.create(name=configuration_type)
    else:
        print("config type exists: %s" % configuration_type)
        configuration_type = query.get()

        # Process agreements
    for agreement in get_agreements(agreement_name):
        print("Processing %s: %s" % (agreement["company"]["name"], agreement["name"]))

        # Create our company, if doesn't exist
        query = Company.select().where(Company.id == agreement["company"]["id"])
        if not query.exists():
            company = Company.create(
                id=agreement["company"]["id"], name=agreement["company"]["name"]
            )
        else:
            company = query.get()

        # Create our agreement, if doesn't exist

        query = Agreement.select().where(Agreement.id == agreement["id"])
        if not query.exists():
            agreement = Agreement.create(
                id=agreement["id"], name=agreement["name"], company=company
            )
        else:
            agreement = query.get()

        # Create our configurations, if doesn't exist
        configurations = get_configurations(
            company_id=company.id, configuration_type=configuration_type.name
        )
        for configuration in configurations:
            query = Configuration.select().where(
                Configuration.id == configuration["id"]
            )
            if not query.exists():
                if "deviceIdentifier" in configuration.keys():
                    if configuration["deviceIdentifier"] == "":
                        device_id = None
                    else:
                        device_id = configuration["deviceIdentifier"]
                else:
                    device_id = None
                Configuration.create(
                    id=configuration["id"],
                    name=configuration["name"],
                    configuration_type=configuration_type,
                    company=company,
                    device_id=device_id,
                )

        # Create our additions
        additions = get_additions(
            agreement_id=agreement.id, product_identifier=product_identifier
        )

        for addition in additions:
            query = Addition.select().where(Addition.id == addition["id"])
            if not query.exists():
                Addition.create(
                    id=addition["id"],
                    name=addition["product"]["identifier"],
                    agreement=agreement,
                    quantity=addition["quantity"],
                    less_included=addition["lessIncluded"],
                )


def init_products():
    products = {}

    products["phones"] = {
        "agreement_name": "ITSG - VOIP",
        "product_identifier": "VOIP - User Licenses",
        "configuration_type": "Managed Phone",
    }
    products["workstations"] = {
        "agreement_name": "MSP%",
        "product_identifier": "Add Workstations%",
        "configuration_type": "Managed Workstation",
    }
    products["servers"] = {
        "agreement_name": "MSP%",
        "product_identifier": "Add Servers%",
        "configuration_type": "Managed Server",
    }

    for key, val in products.items():

        products[key] = process_products(
            agreement_name=val["agreement_name"],
            product_identifier=val["product_identifier"],
            configuration_type=val["configuration_type"],
        )
    return products
