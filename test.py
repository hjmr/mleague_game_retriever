import os
import re
import json
import hashlib
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


def get_game_log(session, gameid, auth_info):
    gamelog_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://m-league.jp",
        "Referer": "https://m-league.jp/",
    }
    md5pass = hashlib.md5(auth_info["password"].encode()).hexdigest()
    passstr = f"password={md5pass}"
    print(passstr)
    response = requests.post(game_base_url + gameid, headers=gamelog_headers, data=passstr)
    assert response.status_code == 200, f"{response.status_code} {response.text}"
    sessionId = response.cookies.get("Set-Cookie")
    log_json = None
    game_log = re.search(r"UMP_PLAYER.init\([^']+'([^']+)'.+", response.text)
    if game_log is not None:
        log_json = json.loads(game_log.group(1))
    return log_json, sessionId


if __name__ == "__main__":
    session = requests.Session()
    auth_email = os.getenv("MLEAGUE_ACCOUNT")
    auth_password = os.getenv("MLEAGUE_PASSWORD")
    auth_info = {"email": auth_email, "password": auth_password}
    response = signin(session, auth_info)
    print(response)

    gameid = "L001_S016_0097_01A"
    game_log, sessionId = get_game_log(session, gameid, auth_info)
    print(sessionId)
