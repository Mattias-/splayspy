import time
import json
import os
import datetime

from twisted.internet import defer, task
from rethinkdb import r

import gethttp
import utils

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

    def diffPrograms(self, source_prog_list):
        t = self.db_table

        #filter svtplay
        db_list = t.without('episodes').run()

        (new, old, current) = utils.diffDicts(source_prog_list, db_list,
                                              utils.progHash)
        if new: print 'added', new

        now = datetime.datetime.utcnow().isoformat()
        for d in new:
            d['first_seen'] = d['last_seen'] = now
            d['seen_counter'] = 1
            d['episodes'] = []
        t.insert(new).run()

        for d in current:
            t.filter({'channel':d['channel'], 'id':d['id']}).update({
                'seen_counter': r.row['seen_counter'] + 1,
                'last_seen': now}).run()

        print 'source_prog_list', len(source_prog_list)
        return source_prog_list

    def updatePrograms(self):
        d = gethttp.getPageData(self.all_programs_url)
        d.addCallback(self.getSourcePrograms)
        d.addCallback(self.diffPrograms)
        return d

    def updateProgramEpisodes(self, pl):
        print "Start getting the episodes"
        def defGen(pl):
            #pl = [pl.pop(), pl.pop()]
            for p in pl:
                d = self.getProgramEpisodes(p)
                d.addCallback(self.diffEpisodes, p)
                yield d
        defs = []
        coop = task.Cooperator()
        work = defGen(pl)
        maxRun = 5
        for i in xrange(maxRun):
            d = coop.coiterate(work)
            defs.append(d)
        dl = defer.DeferredList(defs)
        return dl

    def diffEpisodes(self, episodes, program):
        print program['channel'], program['name'], len(episodes)

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

        if new: print 'added', new

        db_program.update({'episodes': new+old+current}).run()

    def getProgramEpisodes(self, program):
        url = self.episodes_url % str(program['id'])
        #TODO bench, tune persistentConn
        d = gethttp.requestGet(url)
        #d = gethttp.getPageData(url)
        d.addCallbacks(self.getSourceEpisodes, self.printerror, errbackArgs=[program])
        #d.addErrback(self.printerror, program)
        return d

    def printerror(self, failure, program):
        print failure, program

