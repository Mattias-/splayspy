import logging

import svtplay
import tv4play

log = logging.getLogger("splays")


def main():
    log.setLevel(logging.DEBUG)
    fmt = '%(asctime)s::%(name)s::%(levelname)s::%(message)s'
    formatter = logging.Formatter(fmt)

    fh = logging.FileHandler("splays.log", mode='w')
    fh.setFormatter(formatter)
    log.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    log.addHandler(sh)

    log.info("Started splays scraper & parser")

    channels = [
        svtplay.SVTplay(),
        #tv4play.TV4play(),
    ]
    log.info("Channels: %s" % channels)
    for c in channels:
        pl = c.getPrograms()
        #c.updateProgramEpisodes(pl)

if __name__ == '__main__':
    main()
