import bs4
from twisted.internet import defer

import core

class SVTplay(core.Channel):
    def __init__(self):
        self.prog_list = []
        self.base_url = 'http://www.svtplay.se'
        self.all_programs_url = '%s/program' % self.base_url
        self.program_url = '%s/%%s' % self.base_url
        self.episodes_url = '%s/%%s/?tab=episodes&sida=8' % self.base_url
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
            all_eps.append(new_episode)
            #print new_episode
        return all_eps
