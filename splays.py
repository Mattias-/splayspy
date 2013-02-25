
from twisted.internet import reactor, defer

import svtplay

def finish(ign):
    print 'finished'
    reactor.stop()

def main():
    svt = svtplay.SVTplay()

    d1 = svt.updatePrograms()
    #d2 = svt.updatePrograms()
    d1.addCallback(svt.updateProgramEpisodes)
    defs = [d1]

    dl = defer.DeferredList(defs)
    dl.addBoth(finish)
    reactor.run()

main()
