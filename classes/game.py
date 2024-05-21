class Game:
    def __init__(self):
        self.game_id = None
        self.type = None
        self.winner = None
        self.duration = None
        self.date = None

        self.players = None

        self.time_frames = []

    def __repr__(self):
        return f'Game(game_id={self.game_id}, duration={self.duration // 60}m{self.duration % 60}s, date={self.date}, winner={self.winner})'