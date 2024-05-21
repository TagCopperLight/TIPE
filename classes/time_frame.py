class TimeFrame:
    """
    A time frame of a minute.
    """
    
    def __init__(self, length):
        self.length = length
        self.interactions = [[[False, False] for _ in range(5)] for _ in range(5)]
        self.deaths = [[False for _ in range(5)] for _ in range(2)]