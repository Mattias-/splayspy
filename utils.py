import time
import urllib2

import bs4
from twisted.internet import reactor, defer

import gethttp
import core

class SVTplay(core.Channel):
    def __init__(self):
        self.prog_list = set()
        self.base_url = 'http://www.svtplay.se'
        self.all_programs_url = '%s/program' % self.base_url
        self.program_url = '%s/%%s' % self.base_url
        self.episodes_url = '%s?tab=episodes&sida=6'
        self.name = 'svtplay'

    def getSourcePrograms(self, raw):
        d = defer.Deferred()
        page = bs4.BeautifulSoup(raw)
        links = page.find_all('a', class_='playAlphabeticLetterLink')

        source_prog_list = set()
        for link in links:
            name = link.contents[0]
            url = "".join([self.base_url, link.get('href')])
            id = link.get('href')[1:]
            program = core.Program(id, name, url, self)
            source_prog_list.add(program)
        return source_prog_list

    def diffPrograms(self, source_prog_list):
        #TODO get from db
        if self.prog_list:
            a = self.prog_list.pop()
            a = self.prog_list.pop()
        #print 'source_prog_list', len(source_prog_list)
        #print 'self.prog_list', len(self.prog_list)
        new = source_prog_list - self.prog_list
        removed = self.prog_list - source_prog_list
        #print '%s new %s' % (len(new), new)
        #print '%s removed %s' % (len(removed), removed)
        #TODO Make changes to database with new, removed
        self.prog_list = source_prog_list
        return self.prog_list

    def updatePrograms(self):
        d = gethttp.getPageData(self.all_programs_url)
        d.addCallback(self.getSourcePrograms)
        d.addCallback(self.diffPrograms)
        return d

    def updateProgramEpisodes(self, pl):
        defs = []
        for p in pl:
            defs.append(p.updateEpisodes())
        #defs.append(pl.pop().updateEpisodes())
        #defs.append(pl.pop().updateEpisodes())
        dl = defer.DeferredList(defs)
        return dl

    def getSourceEpisodes(self, raw):
        print 'got raw', len(raw)
        return ['e1','e2','e3','e4']

    def getProgramEpisodes(self, program):
        prog_url = self.program_url % str(program.id)
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

    def1 = svt.updatePrograms()
    def1.addCallback(svt.updateProgramEpisodes)
    defs = [def1]

    dl = defer.DeferredList(defs)
    dl.addBoth(finish)
    reactor.run()

main()

