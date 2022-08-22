import requests


def getcvrinfo(cvr):

    url = f"https://apicvr.dk/api/v1/{cvr}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


print(getcvrinfo(cvr=12345678))
