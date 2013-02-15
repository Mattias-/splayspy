import time
import urllib2

import bs4
from twisted.internet import reactor, defer

import gethttp
import core

svtplay = {'programurl': "http://www.svtplay.se%s",
          'episodeurl': "aaa%s"}

class SVTplay(core.Channel):
    def __init__(self):
        self.prog_list = set()
        self.base_url = 'http://www.svtplay.se'
        self.program_url = '%s/program' % self.base_url

    def getSourcePrograms(self, raw):
        d = defer.Deferred()
        page = bs4.BeautifulSoup(raw)
        links = page.find_all('a', class_='playAlphabeticLetterLink')

        source_prog_list = set()
        #print links
        for link in links:
            name = link.contents[0]
            url = "".join([self.base_url, link.get('href')])
            id = link.get('href')[1:]
            channel ='svtplay'
            program = core.Program(id, name, url, channel)
            #print program
            source_prog_list.add(program)
        return source_prog_list

    def diffPrograms(self, source_prog_list):
        if self.prog_list:
            a = self.prog_list.pop()
            a = self.prog_list.pop()
        print 'source_prog_list', len(source_prog_list)
        print 'self.prog_list', len(self.prog_list)
        new = source_prog_list - self.prog_list
        removed = self.prog_list - source_prog_list
        print '%s new %s' % (len(new), new)
        print '%s removed %s' % (len(removed), removed)
        # Make changes to database with new, removed
        self.prog_list = source_prog_list

    def updatePrograms(self):
        d = gethttp.getPageData(self.program_url)
        d.addCallback(self.getSourcePrograms)
        d.addCallback(self.diffPrograms)
        return d

    def updateAll(self, raw):
        self.getSourceProrams(raw, self.diffPrograms)

def th(res):
    print res[0:100], res[-10:]

def finish(ign):
    print 'finished'
    reactor.stop()

def main():
    start = time.time()
    #print time.time() - now

    svt = SVTplay()
    defs = [svt.updatePrograms()]
    dl = defer.DeferredList(defs)
    dl.addBoth(finish)

    reactor.run()

main()


#gethttp.requestGet(url, programs)
#import urllib2
#raw = urllib2.urlopen(url).read()
#page = bs4.BeautifulSoup(raw)
#links = page.find_all('a', class_='playAlphabeticLetterLink')
#for link in links:
#    print link.get('href'), link.contents[0]
