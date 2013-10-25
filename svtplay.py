import bs4

import core


class SVTplay(core.Channel):
    def __init__(self):
        self.name = 'svtplay'
        self.base_url = 'http://www.svtplay.se'
        self.all_programs_url = '%s/program' % self.base_url
        self.program_url = '%s/%%s' % self.base_url
        self.episodes_url = '%s/%%s/?tab=episodes&sida=8' % self.base_url
        super(core.Channel, self).__init__()

    def getSourcePrograms(self, raw):
        page = bs4.BeautifulSoup(raw)
        nodes = page.find_all('a', class_='playAlphabeticLetterLink')
        progs = []
        for n in nodes:
            program = {}
            program['channel'] = self.name
            program['id'] = n.get('href')[1:]
            program['name'] = n.contents[0]
            program['url'] = "".join([self.base_url, n.get('href')])
            progs.append(program)
        return progs

    def getSourceEpisodes(self, raw):
        page = bs4.BeautifulSoup(raw)
        nodes = page.find_all('article', class_='svtMediaBlock')
        eps = []
        for n in nodes:
            episode = {}
            episode['name'] = n['data-title']
            episode['url'] = "".join([self.base_url,
                                      n.find('a', class_='playLink')['href']])
            data = {}
            data['published'] = n.find('time')['datetime']
            data['descr'] = n['data-description']
            data['length'] = n['data-length']
            data['img'] = n.find('img', class_='playGridThumbnail')['src']
            episode['data'] = data
            eps.append(episode)
        return eps
