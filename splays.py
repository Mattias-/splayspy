import logging

import svtplay
import tv4play

log = logging.getLogger("splays")

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
    tv4 = tv4play.TV4play()
    channels = [\
                svt,
  #              tv4,
                ]
    log.info("Channels: %s" % channels)

    for c in channels:
        pl = c.updatePrograms()
        c.updateProgramEpisodes(pl)

main()
