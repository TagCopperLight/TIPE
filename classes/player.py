class Player:
    def __init__(self):
        self.summoner_name = None
        self.champion = None
        self.elo = None

    def __repr__(self):
        return f'Player(summoner_name={self.summoner_name}, champion={self.champion}, elo={self.elo})'