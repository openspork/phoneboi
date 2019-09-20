from threading import Lock
from time import mktime
from datetime import datetime, timezone
from json import dumps, loads
from requests import get
from flask import Flask, redirect, render_template, url_for
from util.process_api import *
from flask_socketio import SocketIO, emit
from models import *

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

thread = None
thread_lock = Lock()


@socketio.on("update", namespace="/test")
def update(message):
    print("UUID received " + message["data"])


@socketio.on("connect", namespace="/test")
def test_connect():
    print("Client connected")
    start_heartbeat_thread()
    emit("server_heartbeat", {"data": "Connected", "count": 0})


@socketio.on("disconnect", namespace="/test")
def test_disconnect():
    print("Client disconnected")


def heartbeat_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(1)
        count += 1
        utc_datetime = datetime.now(timezone.utc)
        utc_datetime_for_js = int(mktime(utc_datetime.timetuple())) * 1000
        socketio.emit(
            "heartbeat",
            {"datetime": utc_datetime_for_js, "count": count},
            namespace="/test",
        )


def start_heartbeat_thread():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=heartbeat_thread)


@app.route("/init")
def init():
    init_products()
    return redirect(url_for("index"))


@app.route("/")
def index():
    # agreements = []
    companies = {}
    for agreement in Agreement.select():

        agreement_fmt = {}

        agreement_fmt["company_name"] = agreement.company.name
        agreement_fmt["agreement_name"] = agreement.name

        addition_types = {}
        # Iterate through all additions
        for addition in agreement.additions:
            # If the addition type does not exist, create
            if not addition.configuration_type.name in addition_types.keys():
                addition_types[addition.configuration_type.name] = {
                    "quantity_sum": addition.quantity,
                    "less_included_sum": addition.less_included,
                }

            # Otherwise add to current sums
            else:
                addition_types[addition.configuration_type.name]["quantity_sum"] = (
                    addition_types[addition.configuration_type.name]["quantity_sum"]
                    + addition.quantity
                )
                addition_types[addition.configuration_type.name][
                    "less_included_sum"
                ] = (
                    addition_types[addition.configuration_type.name][
                        "less_included_sum"
                    ]
                    + addition.less_included
                )

            # Get the number of corresponding configurations
            addition_types[addition.configuration_type.name]["configuration_sum"] = len(
                Configuration.select().where(
                    (Configuration.configuration_type == addition.configuration_type)
                    & (Configuration.company == agreement.company)
                )
            )

        agreement_fmt["addition_types"] = addition_types

        # map agreement against company
        # If the company does not exist, create
        if not agreement.company.name in companies.keys():
            companies[agreement.company.name] = []

        companies[agreement.company.name].append(agreement_fmt)

        # agreements.append(agreement_fmt)

    # return render_template("index.html", agreements=agreements)
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


if __name__ == "__main__":
    socketio.run(app, debug=True)
