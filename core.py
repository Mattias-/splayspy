

class Channel():
    def __init__(self):
        pass
    def findAddNewPrograms(self):
        pass

class Program():
    def __init__(self, id, name, url, channel):
        self.id = id
        self.name = name
        self.url = url
        self.channel = channel

    def __hash__(self):
        return hash(self.id)+hash(self.name)+hash(self.channel)+hash(self.url)

    def findAddNewEpisodes():
        pass
    def getEpisodes():
        pass

class Episode():
    def __init__():
        pass
