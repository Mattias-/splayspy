from twisted.internet import threads

class Channel():
    def __init__(self):
        pass

    def __repr__(self):
        return "<Channel %s>" % self.name

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

    def __eq__(self, other):
        return self.id == other.id and self.channel == other.channel

    def __repr__(self):
        return "<Program %s @ %s>" % (self.id, self.channel)

    def diffEpisodes(self, episodes):
        print self.id, episodes

    def updateEpisodes(self):
        d = self.channel.getProgramEpisodes(self)
        d.addCallback(self.diffEpisodes)
        return d

class Episode():
    def __init__():
        pass
