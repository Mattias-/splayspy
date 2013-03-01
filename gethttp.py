from twisted.internet import defer, reactor, protocol
import twisted.web.client as web_client
import twisted.web._newclient as new_web_client

def cbRequest(response):
    class SimpleReceiver(protocol.Protocol):
        def __init__(self, finished):
            self.finished = finished
            self.body = []

        def dataReceived(self, bytes):
            self.body.append(str(bytes))

        def connectionLost(self, reason):
            if reason.check(new_web_client.ResponseDone):
                self.finished.callback(''.join(self.body))
            else:
                self.finished.errback(reason)

    finished = defer.Deferred()
    response.deliverBody(SimpleReceiver(finished))
    return finished

pool = web_client.HTTPConnectionPool(reactor, persistent=True)
agent = web_client.Agent(reactor, pool=pool)

def requestGet(url):
    d = agent.request('GET', url)
    d.addCallback(cbRequest)
    return d

