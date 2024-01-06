import socket
import sys
import re
import json
import datetime
import pathlib
import pydirectinput
import subprocess
import time
import logging


pydirectinput.PAUSE = 0.01
LOADING_SCREEN_TIME = 9
LOADING_GAME_TIME = 15
CONTINUE_BUTTON = (960, 640)

log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')

def get_stream(game_id, game_duration):

    text = ""
    state = "LoadingScreen" # LoadingScreen, LoadingGame, WaitingMinions, Receiving, Closing
    start_time = datetime.datetime.now()

    log.info("Starting app ...")
    game_path = pathlib.Path(f"./get_data/games/{game_id}.bat")
    subprocess.run(game_path)
    log.info("Waiting for app to load ...")
    time.sleep(LOADING_SCREEN_TIME)
    log.info("App started and loaded")

    log.info("Connecting to app ...")
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect(("127.0.0.1", 34243))
        soc.setblocking(0)
    except ConnectionRefusedError:
        raise ConnectionRefusedError("App not started")
    log.info("Connected to app")

    log.info("Focusing app ...")
    pydirectinput.click(*CONTINUE_BUTTON)

    log.info("Waiting for game to start ...")
    try:
        while state != "Closing":
            if state == "LoadingGame":
                if datetime.datetime.now() - start_time > datetime.timedelta(seconds=LOADING_GAME_TIME):
                    log.info("Game loaded")
                    state = "WaitingMinions"
                    for _ in range(3):
                        pydirectinput.press('=')
                    log.info("Waiting for minions to spawn ...")
            elif state == "Receiving":
                if datetime.datetime.now() - start_time > datetime.timedelta(seconds=game_duration - 40)/8:
                    log.info("Game finished, closing app")
                    state = "Closing"
            try:
                if soc.recv(1):
                    size = soc.recv(4)
                    size = int.from_bytes(size, byteorder=sys.byteorder)
                    data = soc.recv(size)
                    text += f"{datetime.datetime.timestamp(datetime.datetime.now())}\n"
                    data = data.decode("utf-8")
                    text += data

                    if state == "LoadingScreen" and "OnGameStart" in data:
                        log.info("Game started")
                        state = "LoadingGame"
                        start_time = datetime.datetime.now()
                        pydirectinput.press('p')
                        log.info("Waiting for game to load ...")
                    elif state == "WaitingMinions" and "OnNexusCrystalStart" in data:
                        log.info("Minions spawned")
                        state = "Receiving"
                        start_time = datetime.datetime.now()
                        log.info("Receiving data ...")
            except BlockingIOError:
                pass

    except ConnectionError:
        if state != "Closing":
            raise ConnectionError("Connection closed unexpectedly")
        soc.close()

    log.info("Closing app ...")
    pydirectinput.moveTo(*CONTINUE_BUTTON)
    pydirectinput.mouseDown()
    time.sleep(0.1)
    pydirectinput.mouseUp()

    log.info("App closed")

    return text

def parse_data(text):
    log.info("Parsing data ...")
    text = re.sub("\neventname\"", "\n{\n\n\t\"eventname\"", text)
    text = re.sub("^eventname\"", "{\n\n\t\"eventname\"", text)
    timed_events = re.findall(r"([0-9]*\.[0-9]+\n{(?:.|\n)*?})\n\d", text[1:])

    total_events = []

    for timed_event in timed_events:
        timestamp = timed_event.split("\n")[0]
        events = re.findall(r"{(?:.|\n)*?}", timed_event)

        events = [json.loads(event) for event in events]
        for event in events:
            event["timestamp"] = "1" + timestamp
        
        total_events += events

    log.info("Data parsed")

    return total_events

def generate_json(game_id, game_duration):
    text = get_stream(game_id, game_duration)
    
    events = parse_data(text)

    data_folder = pathlib.Path("get_data/data/")
    file_name = data_folder / f"{game_id}.json"

    log.info("Saving data ...")
    with open(file_name, "w") as file:
        json.dump(events, file, indent=4)
    log.info("Data saved")
    
    return events

if __name__ == "__main__":
    try:
        generate_json("6751494867", 8*60+39)
    except Exception as e:
        log.error(e)
        raise e