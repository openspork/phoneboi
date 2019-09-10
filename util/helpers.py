from json import dumps, loads
from requests import get

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