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

    def updateProgramEpisodes(self, pl):
        #pl = [pl.pop(), pl.pop()]
        errors = []
        for p in pl:
            url = self.episodes_url % str(p['id'])
            try:
                f = urllib2.urlopen(url)
                episodes = self.getSourceEpisodes(f)
                self.diffEpisodes(episodes, p)
            except urllib2.HTTPError as e:
                log.error("Program %s, %s" % (p,e))
                errors.append(p)

    def diffEpisodes(self, episodes, program):
        pass
        log.info('Diffing episodes of %s %s, count: %d' % (program['channel'],
                                                           program['name'],
                                                           len(episodes)))
        starttime = time.time()
        if episodes:
            #t = self.db_table
            #db_program = t.filter({'channel':program['channel'],
            #                       'id': program['id']})

            #db_res = db_program.pluck('episodes').run()
            for d in db_res:
                db_list = d['episodes']
            #if len(db_res) == 1:
            #    db_list = db_res[0]
            #else:
            #    raise Exception('too many results')

            (old, new, current) = utils.diffDicts(db_list, episodes,
                                                  utils.episodeHash)
            now = datetime.datetime.utcnow().isoformat()
            for d in new:
                d['first_seen'] = d['last_seen'] = now
                d['seen_counter'] = 1
            for d in current:
                d['last_seen'] = now
                d['seen_counter'] += 1

            if new:
                log.info('Added episodes to %s %s: %s' % (self.name,
                                                          program['id'],
                                                          [n['name'] for n in new]))

            db_program.update({'episodes': new+old+current}).run()
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
