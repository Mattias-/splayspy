
import logging

from twisted.internet import reactor, defer

import svtplay

log = logging.getLogger("splays")

def finish(ign):
    log.info("Finished!")
    reactor.stop()

def main():
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s::%(name)s::%(levelname)s::%(message)s')
    fh = logging.FileHandler("splays.log", mode='w')
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    log.addHandler(fh)
    log.addHandler(sh)

    log.info("Started splays scraper & parser")

    svt = svtplay.SVTplay()
    channels = [svt]
    log.info("Channels: %s" % channels)

    defs = []
    for ch in channels:
        d = ch.updatePrograms()
        d.addCallback(ch.updateProgramEpisodes)
        defs.append(d)
    dl = defer.DeferredList(defs)
    dl.addBoth(finish)

    reactor.run()

main()
