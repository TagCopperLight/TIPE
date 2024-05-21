import re
import json
import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')

with open('saved_games.json', 'r') as f:
    saved_games = json.load(f)


class HtmlParser:
    def __init__(self, html):
        self.html = html
        self.page = -1
        self.tables = self.get_tables()
    
    def get_tables(self):
        return re.findall(r"<table.*>(?:.|\n)*?<\/table>", self.html)
    
    def write_tables(self):
        with open("tables.html", "w") as f:
            f.write(self.tables[0])
    
    def read_table(self):
        with open("tables.html", "r") as f:
            return f.read()

class Browser:
    def __init__(self):
        log.info("Getting driver...")
        self.service = Service(executable_path='./drivers/geckodriver')
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument('--headless')
        log.info("Starting driver...")
        self.driver = webdriver.Firefox(service=self.service, options=self.options)
        self.driver.install_addon('./drivers/ublock_origin-1.53.0.xpi', temporary=True)

    def get_parser(self, url):
        log.info("Getting html...")
        self.driver.get(url)
        return HtmlParser(self.driver.page_source)
    
    def write_html(self, parser):
        log.info("Writing html...")
        with open("data.html", "w") as f:
            f.write(parser.html)
    
    def quit(self):
        log.info("Closing driver...")
        self.driver.quit()

class Player:
    def __init__(self, html):
        self.html = html
        self.champion = self.get_champion()
        self.summoner = self.get_summoner()
        self.elo = self.get_elo()
    
    def get_champion(self):
        champion = re.findall(r'<img src="(.*?)" alt="(.*?)" title="(.*?)">', self.html)[0][1]
        return champion
    
    def get_summoner(self):
        summoner = re.findall(r'<div class="name">(?:.|\n)*?<\/div>', self.html)[0].replace('<div class="name">', '').replace('</div>', '')
        return re.search(r"\s*(.*?)\s*$", summoner).group(1)
    
    def get_elo(self):
        elo = re.findall(r'<div class="subname">(?:.|\n)*?<\/i>', self.html)[0].replace('<div class="name">', '').replace('</i>', '')
        return re.search(r"\s*(.*?)\s*$", elo).group(1)

class Game:
    def __init__(self, table, browser, page):
        self.table = table
        self.browser = browser
        self.page = page
        self.match_id = self.get_match_id()
        self.type = self.get_type()
        self.winner = self.get_winner()
        self.duration = self.get_duration()
        self.date = self.get_date()
        self.players = self.get_players()

        self.file = self.get_file()


    def get_match_id(self):
        match_id = re.findall(r'<a href="(.*?)">\s*', self.table)[0].replace('/match','')
        return match_id

    def get_type(self):
        type = re.findall(r'<span class="queueName">(?:.|\n)*?<\/span>', self.table)
        type = type[0].replace('<span class="queueName">', '').replace('</span>', '')
        return re.search(r"\s*(.*?)\s*$", type).group(1)
    
    def get_winner(self):
        winner = re.findall(r'<th class="text-left-dark-only"(?:.|\n)*?<span(.*?)>(.*?)<\/span>', self.table)
        return "blue" if winner[0][1] == "Victory" else "red"
    
    def get_duration(self):
        duration = re.findall(r'<span class="gameDuration">(?:.|\n)*?<\/span>', self.table)
        duration = duration[0].replace('<span class="gameDuration">', '').replace('</span>', '')
        return re.search(r"\s*(.*?)\s*$", duration).group(1)
    
    def get_date(self):
        timestamp = re.findall(r'<i data-timestamp-date="(.*?)">', self.table)
        return timestamp[0]
    
    def get_players(self):
        players = re.findall(r'<div class="relative">(?:.|\n)*?<\/td>', self.table)
        players = [Player(player) for player in players]
        return players
    
    def get_file(self):
        if "twitchSpectatePopup" in self.table:
            return "twitch"
        file_data = re.findall(r'<a href="#" data-rel="spectatePopup" data-width="640" class="poplight spectatePopupLink" data-spectate-link="(.*)" data-spectate-platform="(.*)" data-spectate-gameid="(.*)" data-spectate-encryptionkey="(.*)" data-spectate-endpoint="(.*)">', self.table)
        return file_data[0]
    
    def write_game(self):
        for game in saved_games:
            if game['match_id'] == self.match_id:
                return
        
        saved_games.append({'match_id': self.match_id, 'type': self.type, 'winner': self.winner, 'duration': self.duration, 'date': self.date, 'players': [{'champion': player.champion, 'summoner': player.summoner, 'elo': player.elo} for player in self.players]})

    def write_file(self):
        if self.file == "twitch":
            return
        
        with open('games/batch_data.json', 'r') as f:
            batch_data = json.load(f)
        
        batch_data.append({'id': self.file[2], 'arg1': self.file[4], 'arg2': self.file[3], 'arg3': self.file[2], 'arg4': self.file[1]})

        with open('games/batch_data.json', 'w') as f:
            json.dump(batch_data, f, indent=4)

def get_games(parser, browser):
    games = []
    for table in parser.tables:
        games.append(Game(table, browser, parser.page))
    return games

def record_data(browser, page):
    log.info(f"Parsing html... {page}/50")
    if page == 1:
        parser = browser.get_parser('https://www.leagueofgraphs.com/replays/all/iron')
    else:
        parser = browser.get_parser(f'https://www.leagueofgraphs.com/replays/all/iron/page-{page}')

    parser.page = page
    return parser

def main():
        browser = Browser()
        for page in range(1, 51):
            parser = record_data(browser, page)
            games = get_games(parser, browser)
            for game in games:
                game.write_game()
                game.write_file()

        with open('saved_games.json', 'w') as f:
            json.dump(saved_games, f, indent=4)
        
        browser.quit()

if __name__ == "__main__":
    main()
