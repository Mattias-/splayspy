import time
import urllib2
import pickle
import json
import os
import datetime

import bs4
from twisted.internet import reactor, defer

import gethttp
import core

class SVTplay(core.Channel):
    def __init__(self):
        self.prog_list = []
        self.base_url = 'http://www.svtplay.se'
        self.all_programs_url = '%s/program' % self.base_url
        self.program_url = '%s/%%s' % self.base_url
        self.episodes_url = '%s?tab=episodes&sida=8'
        self.name = 'svtplay'

    def getSourcePrograms(self, raw):
        d = defer.Deferred()
        page = bs4.BeautifulSoup(raw)
        links = page.find_all('a', class_='playAlphabeticLetterLink')

        source_prog_list = []
        for link in links:
            name = link.contents[0]
            url = "".join([self.base_url, link.get('href')])
            id = link.get('href')[1:]
            program = {}
            program['name'] = name
            program['url'] = url
            program['id'] = id
            program['channel'] = self.name
            source_prog_list.append(program)
        return source_prog_list

    def diffPrograms(self, source_prog_list):
        db_list = []
        # get programs from db
        filename = 'db/%s.txt' % self.name
        try:
            with open(filename, 'r') as infile:
                db_list = json.load(infile)
        except IOError as e:
            print 'no file %s' % filename
            os.makedirs('db/%s_programs' % self.name)
            print 'created program dir'

        (new, removed, both) = core.diffDicts(source_prog_list, db_list,
                                              core.progHash)
        if new: print 'new', new
        if removed: print 'removed', removed

        # insert/update new
        db_list.extend(new)
        #set removed
        for r in removed:
            i = db_list.index(r)
            db_list[i]['removed'] = True
        with open(filename, 'w') as outfile:
            json.dump(db_list, outfile)

        print 'source_prog_list', len(source_prog_list)
        return source_prog_list

    def updatePrograms(self):
        d = gethttp.getPageData(self.all_programs_url)
        d.addCallback(self.getSourcePrograms)
        d.addCallback(self.diffPrograms)
        return d

    def updateProgramEpisodes(self, pl):
        defs = []
        #pl = [pl.pop(), pl.pop()]
        #print 'updating eps of', pl
        for p in pl:
            d = self.getProgramEpisodes(p)
            d.addCallback(self.diffEpisodes, p)
            defs.append(d)
        dl = defer.DeferredList(defs)
        return dl

    def diffEpisodes(self, episodes, program):
        print program['channel'], program['name'], len(episodes)
        db_list = []

        # get programs from db
        filename = 'db/%s_programs/%s.txt' % (program['channel'], program['id'])
        try:
            with open(filename, 'r') as infile:
                db_list = json.load(infile)
        except IOError as e:
            print 'no file %s' % filename
        current = [d for d in db_list if not d.get('removed', False)]
        removed = [d for d in db_list if d.get('removed', False)]

        (add, remove, both) = core.diffDicts(episodes, current,
                                             core.episodeHash)
        (new, old_removed, readded) = core.diffDicts(add, removed,
                                                     core.episodeHash)
        if new: print 'added', new
        if remove: print 'removed', remove
        if readded: print 'readded', readded
        # add new items in db
        # update 'removed'=True for remove items in db
        # update 'removed'=False for readded items in db
       
        db_list = both+new
        #set removed
        for r in remove:
            r['removed'] = True
            db_list.append(r)

        with open(filename, 'w') as outfile:
            json.dump(db_list, outfile)

    def getSourceEpisodes(self, raw):
        page = bs4.BeautifulSoup(raw)
        eps = page.find_all('article', class_='svtMediaBlock')
        all_eps = []
        for e in eps:
            new_episode = {}
            new_episode['name'] = e['data-title']
            new_episode['url'] = "".join([self.base_url,
                           e.find('a', class_='playLink')['href']])
            data = {}
            data['published'] = e.find('time')['datetime']
            data['descr'] = e['data-description']
            data['length'] = e['data-length']
            data['img'] = e.find('img', class_='playGridThumbnail')['src'] 
            new_episode['data'] = data
            new_episode['added'] = datetime.datetime.utcnow().isoformat()
            new_episode['removed'] = False
            all_eps.append(new_episode)
            #print new_episode
        return all_eps

    def getProgramEpisodes(self, program):
        prog_url = self.program_url % str(program['id'])
        url = self.episodes_url % prog_url
        #TODO bench, tune persistentConn
        d = gethttp.requestGet(url)
        #d = gethttp.getPageData(url)
        d.addCallback(self.getSourceEpisodes)
        d.addErrback(self.printerror, program)
        return d

    def printerror(self, failure, program):
        print failure, program

def finish(ign):
    print 'finished'
    reactor.stop()

def main():
    svt = SVTplay()

    d1 = svt.updatePrograms()
    #d2 = svt.updatePrograms()
    d1.addCallback(svt.updateProgramEpisodes)
    defs = [d1]

    dl = defer.DeferredList(defs)
    dl.addBoth(finish)
    reactor.run()

main()

