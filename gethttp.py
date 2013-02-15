from twisted.internet import defer, reactor
from twisted.web.client import getPage

def getPageData(url, pageCallback):
    d = getPage(url)
    d.addCallback(pageCallback)
    return d

#def listCallback(result):
#    for isSuccess, data in result:
#        if isSuccess:
#            print "Call to %s succeeded with data %s" % (data['url'], str(data))

def finish(ign):
    print 'finished'
    reactor.stop()

def test(jobs):
    defs = []
    for url, pageCallback in jobs:
        defs.append(getPageData(url, pageCallback))
    dl = defer.DeferredList(defs)
    #dl.addCallback(listCallback)
    dl.addCallback(finish)

