import datetime
import time
import logging
import urllib2

import fs_storage as storage
import utils

log = logging.getLogger("splays.core")


class Channel(object):
    def __init__(self):
        pass

    def __repr__(self):
        return "<Channel %s>" % self.name

    def getSourcePrograms(self, raw):
        pass

    def getSourceEpisodes(self, raw):
        pass

    def getPrograms(self):
        f = urllib2.urlopen(self.all_programs_url)
        programs = self.getSourcePrograms(f)
        #programs = [programs.pop(), programs.pop()]
        log.debug("Got %d programs from %s" % (len(programs), self.name))
        self.updatePrograms(programs)
        return programs

    def getEpisodes(self, pl):
        errors = []
        for p in pl:
            url = self.episodes_url % str(p['id'])
            try:
                f = urllib2.urlopen(url)
                episodes = self.getSourceEpisodes(f)
                self.updateEpisodes(p, episodes)
            except urllib2.HTTPError as e:
                log.error("Program %s, %s" % (p,e))
                errors.append(p)

    def updateEpisodes(self, program, episodes):
        starttime = time.time()
        if episodes:
            db_list = storage.get_episodes(program)
            (old, new, current) = utils.diffDicts(db_list, episodes,
                                                  utils.episodeHash)
            if new:
                log.info('Added %d new episodes to %s %s' % (len(new),
                                                             program['channel'],
                                                             program['name']))
                log.debug('New %s %s episodes: %s' % (program['channel'],
                                                      program['name'],
                                                      [e['name'] for e in new]))
            if old:
                log.info('Missing %d old episodes from %s %s' % (len(old),
                                                                 program['channel'],
                                                                 program['name']))
                log.debug('Missing %s %s episodes: %s' % (program['channel'],
                                                          program['name'],
                                                          [e['name'] for e in old]))
            if len(new) == 0 and len(old) == 0:
                log.info('%s %s exact match, no new, no old.' % (program['channel'],
                                                                 program['name']))

            now = datetime.datetime.utcnow().isoformat()
            for episode in new:
                episode['seen'] = [now]
            for episode in current:
                episode['seen'].append(now)
            storage.save_episodes(program, new+old+current)

        totaltime = time.time() - starttime
        log.debug('Diffing episodes of %s %s, time: %s' % (program['channel'],
                                                           program['name'],
                                                           totaltime))

    def updatePrograms(self, source_prog_list):
        starttime = time.time()
        db_list = storage.get_programs(self)
        (new, old, current) = utils.diffDicts(source_prog_list, db_list,
                                              utils.progHash, both_ref=db_list)
        if new:
            log.info('Added %d new %s programs' % (len(new), self.name))
            log.debug('New %s programs: %s' % (self.name, [n['id'] for n in new]))
        if old:
            log.info('Missing %d old %s programs' % (len(old), self.name))
            log.debug('Old %s programs: %s' % (self.name, [o['id'] for o in old]))
        if len(new) == 0 and len(old) == 0:
            log.info('%s exact match, no new, no old.' % self.name)

        now = datetime.datetime.utcnow().isoformat()
        for d in new:
            d['episodes'] = []
            d['seen'] = [now]
        for program in current:
            program['seen'] += [now]

        storage.save_programs(self, new+old+current)

        totaltime = time.time() - starttime
        log.debug('Diffing programs of %s, time: %s' % (self.name, totaltime))
        return source_prog_list
