import re
import json
import time
import random
import argparse
import requests

game_base_url = "https://viewer.ml-log.jp/web/viewer?gameid="


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sessionid", type=str, help="paifu session ID")
    parser.add_argument("-o", "--outdir", type=str, help="output directory")
    return parser.parse_args()


def get_game_log(sessionid, gameid):
    gamelog_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://m-league.jp",
        "Referer": "https://m-league.jp/",
    }
    gamelog_headers["Cookie"] = f"paifuSessionId={sessionid}"
    response = requests.get(game_base_url + gameid, headers=gamelog_headers)
    if response.status_code != 200:
        raise Exception(f"Error: Status code is not 200: {response.status_code}, {response.text}")
    log_json = None
    game_log = re.search(r"UMP_PLAYER.init\([^']+'([^']+)'.+", response.text)
    if game_log is not None:
        log_json = json.loads(game_log.group(1))
    return log_json


def save_game_log(filename, log_json):
    with open(filename, "w") as f:
        json.dump(log_json, f, indent=2, ensure_ascii=False)


def get_gameid(L, S, D, A):
    return f"L{L:03d}_S{S:03d}_{D:04d}_{A:02d}A"


def retrieve_game_log(sessionid, outdir, gameid):
    log_json = get_game_log(sessionid, gameid)
    if log_json is None:
        raise Exception("Error: Could not find valid log.")
    save_game_log(f"{outdir}/{gameid}.json", log_json)


def wait_random(min, max):
    sleep_time = random.uniform(min, max)
    print(f"Sleeping for {sleep_time:.2f} seconds.")
    time.sleep(sleep_time)


def main(sessionid, outdir):
    L = 1  # 現状固定
    for S in range(1, 16):  # シーズン
        D = 1  # 何日めか
        A = 1  # 何試合目か
        while True:
            try:
                gameid = get_gameid(L, S, D, A)
                print(f"Game ID: {gameid} ... ", end="", flush=True)
                retrieve_game_log(sessionid, outdir, gameid)
                print("done.")
                wait_random(3, 10)  # 3-10秒待つ
                A += 1
            except Exception as e:
                print("failed.")
                print(e)
                if A == 1:
                    break
                else:
                    A = 1
                    D += 1
                    continue


if __name__ == "__main__":
    args = parse_args()
    main(args.sessionid, args.outdir)
