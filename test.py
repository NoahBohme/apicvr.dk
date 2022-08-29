import requests


def vismaRatingAPI(cvrNumber):
    url = "https://api.vismarating.com/credit/41013583"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return (response.json()['credit_score'], response.json()['credit_days'])


print(vismaRatingAPI(41013583))
