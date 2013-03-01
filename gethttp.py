from twisted.internet import defer, reactor
from twisted.web.client import getPage
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, HTTPConnectionPool
from twisted.web import _newclient


def getPageData(url):#, pageCallback):
    d = getPage(url)
    return d

class SimpleReceiver(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.body = []

    def dataReceived(self, bytes):
        self.body.append(str(bytes))

    def connectionLost(self, reason):
        if reason.check(_newclient.ResponseDone):
            self.finished.callback(''.join(self.body))
        else:
            print 'Error', reason
            self.finished.errback()

def cbRequest(response):
    finished = defer.Deferred()
    response.deliverBody(SimpleReceiver(finished))
    return finished

pool = HTTPConnectionPool(reactor, persistent=True)
agent = Agent(reactor, pool=pool)

def requestGet(url):
    d = agent.request('GET', url)
    d.addCallback(cbRequest)
    return d

