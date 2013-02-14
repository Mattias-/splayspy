from pprint import pformat

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

class BodyGetter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.data = []

    def dataReceived(self, bytes):
        self.data.append(str(bytes))

    def connectionLost(self, reason):
        #print 'Finished receiving body:', reason.getErrorMessage()
        res = ''.join(self.data)
        self.finished.callback(res)

def cbRequest(response, resCb):
    #print 'Response code:', response.code
    #print 'Response phrase:', response.phrase
    #print 'Response headers:'
    #print pformat(list(response.headers.getAllRawHeaders()))

    finished = Deferred()
    finished.addCallback(resCb)
    response.deliverBody(BodyGetter(finished))
    return finished

def cbShutdown(ignored):
    reactor.stop()

def resultHandler(res):
    #print res
    print res[0:20]
    pass

def requestGet(url, callback):
    agent = Agent(reactor)
    d = agent.request('GET', url)
    d.addCallback(cbRequest, callback)
    d.addBoth(cbShutdown)
    reactor.run()

def requestGet2(urls, callback):
    agent = Agent(reactor)
    for u in urls:
        d = agent.request('GET', u)
        d.addCallback(cbRequest, callback)
        d.addBoth(cbShutdown)
    reactor.run()
#http://technicae.cogitat.io/2008/06/async-batching-with-twisted-walkthrough.html
#requestGet('http://web.student.chalmers.se/~matapp/', resultHandler)
#requestGet('http://www.aftonbladet.se', resultHandler)
#requestGet('http://www.expressen.se', resultHandler)

#requestGet2(['http://www.aftonbladet.se','http://www.expressen.se'], resultHandler)

