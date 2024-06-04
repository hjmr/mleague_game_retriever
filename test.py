import os
import re
import json
import requests

signin_url = "https://api.4anko.com/signin"
game_base_url = "https://viewer.ml-log.jp/web/viewer?gameid="


def signin_check(session):
    signin_stage1_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Accept": "*/*",
        "Access-Control-Request-Headers": "content-type",
        "Access-Control-Request-Method": "POST",
        "Origin": "https://m-league.jp",
        "Referer": "https://m-league.jp/",
    }
    response = session.options(signin_url, headers=signin_stage1_headers)
    assert response.status_code == 200
    return response.headers.get("Access-Control-Allow-Credentials")


def signin(session, auth_info):
    signin_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://m-league.jp",
        "Referer": "https://m-league.jp/",
    }
    response = signin_check(session)
    if response == "true":
        response = session.post(signin_url, headers=signin_headers, data=json.dumps(auth_info))
    assert response.status_code == 200
    return json.loads(response.text)


def get_game_log(cookie, gameid):
    request_headers["Cookie"] = cookie
    response = requests.get(game_base_url + gameid, headers=request_headers)
    assert response.status_code == 200
    log_json = None
    game_log = re.search(r"UMP_PLAYER.init\([^']+'([^']+)'.+", response.text)
    if game_log is not None:
        log_json = json.loads(game_log.group(1))
    return log_json


if __name__ == "__main__":
    auth_email = os.getenv("MLEAGUE_ACCOUNT")
    auth_password = os.getenv("MLEAGUE_PASSWORD")
    response = signin(requests.Session(), {"email": auth_email, "password": auth_password})
    print(response)
