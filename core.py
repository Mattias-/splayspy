import datetime
import time
import logging
import urllib2

from rethinkdb import r

import utils

log = logging.getLogger("splays.core")

class Channel(object):
    def __init__(self):
        r.connect('localhost', 28015)
        self.db_table = r.db('dev').table('programs')

    def __repr__(self):
        return "<Channel %s>" % self.name

    def getSourcePrograms(self, raw):
        pass

    def getSourceEpisodes(self, raw):
        pass

    def updatePrograms(self):
        f = urllib2.urlopen(self.all_programs_url)
        programs = self.getSourcePrograms(f)
        #programs = [programs.pop(), programs.pop()]
        self.diffPrograms(programs)
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
        log.info('Diffing episodes of %s %s, count: %d' % (program['channel'],
                                                          program['name'],
                                                          len(episodes)))
        starttime = time.time()
        if episodes:
            t = self.db_table
            db_program = t.filter({'channel':program['channel'],
                                   'id': program['id']})

            db_res = db_program.pluck('episodes').run()
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
                log.info('Added episodes to %s %s: %s' % (self.name, program['id'],
                                                        [n['name'] for n in new]))

            db_program.update({'episodes': new+old+current}).run()
        totaltime = time.time() - starttime
        log.debug('Diffing episodes of %s %s, time: %s' % (program['channel'],
                                                           program['name'],
                                                           totaltime))

    def diffPrograms(self, source_prog_list):
        starttime = time.time()
        t = self.db_table

        db_list = t.filter({'channel':self.name}).without('episodes').run()

        (new, old, current) = utils.diffDicts(source_prog_list, db_list,
                                              utils.progHash)
        if new:
            log.info('Added new %s programs: %s' % (self.name,
                                                    [n['name'] for n in new]))
            log.debug(new)

        if old:
            log.debug('Missing (old) %s programs: %s' % (self.name,
                                                         [o['id'] for o in old]))
        now = datetime.datetime.utcnow().isoformat()
        for d in new:
            d['first_seen'] = d['last_seen'] = now
            d['seen_counter'] = 1
            d['episodes'] = []
        t.insert(new).run()

        li = [str(p['id']) for p in current]
        js_str = "this.channel == '%s' && %s.indexOf(this.id) >= 0" % (self.name, li)
        t.filter(r.js(js_str)).update({
                'seen_counter': r.row['seen_counter'] + 1,
                'last_seen': now}).run()

        totaltime = time.time() - starttime
        log.debug('Diffing programs of %s, time: %s' % (self.name, totaltime))
        return source_prog_list

