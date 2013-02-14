import time
import urllib2
import bs4

import gethttp
import core

svtplay = {'programurl': "http://www.svtplay.se%s",
          'episodeurl': "aaa%s"}

prog_list = set([])
def programs(raw):
    page = bs4.BeautifulSoup(raw)
    links = page.find_all('a', class_='playAlphabeticLetterLink')
    global prog_list

    source_prog_list = set()
    #print links
    for link in links:
        name = link.contents[0]
        url = link.get('href')
        id = url
        channel ='svtplay'
        program = core.Program(id, name, url, channel)
        #print program
        source_prog_list.add(program)
    #now = time.time()
    #print time.time() - now
    # get stored programs
    # diff
    # add diff
    #print source_prog_list
    #print source_prog_list
#    new = source_prog_list - prog_list
#    removed = prog_list - source_prog_list
#    prog_list = source_prog_list
#    print 'new', new
#    print 'removed', removed

url = 'http://www.svtplay.se/program'
gethttp.requestGet(url, programs)

#import urllib2
#raw = urllib2.urlopen(url).read()
#page = bs4.BeautifulSoup(raw)
#links = page.find_all('a', class_='playAlphabeticLetterLink')
#for link in links:
#    print link.get('href'), link.contents[0]
