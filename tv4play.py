import bs4

import core


class TV4play(core.Channel):
    def __init__(self):
        self.name = 'tv4play'
        self.base_url = 'http://www.tv4play.se'
        self.all_programs_url = '%s/program?content-type=a-o' % self.base_url
        self.program_url = '%s/program/%%s' % self.base_url
        self.episodes_url = '%s/videos/search?node_nids=%%s&page=1&per_page=999&type=video' % self.base_url
        super(core.Channel, self).__init__()

    def getSourcePrograms(self, raw):
        page = bs4.BeautifulSoup(raw)
        aolist = page.find_all('ul', class_='a-o-list')
        nodes = aolist[0].find_all('a')
        progs = []
        for n in nodes:
            program = {}
            program['channel'] = self.name
            program['id'] = n.get('href').split('/')[-1]
            program['name'] = n.contents[0]
            program['url'] = "".join([self.base_url, n.get('href')])
            progs.append(program)
        return progs

    def getSourceEpisodes(self, raw):
        page = bs4.BeautifulSoup(raw)
        nodes = page.find_all('li', class_='video-panel')
        eps = []
        for n in nodes:
            video_info = n.find('div', class_='video-info')
            a_node = video_info.find('h3', class_='video-title').find('a')
            episode = {}
            episode['name'] = a_node.contents[0]
            episode['url'] = "".join([self.base_url, a_node['href']])
            data = {}
            data['published'] = video_info.find('p', class_='date').contents[0]
            descr = video_info.find('p', class_='video-description').find('span').contents
            if descr:
                data['descr'] = descr[0]
            data['img'] = n.find('p', class_='video-picture').find('img')['src']
            episode['data'] = data
            eps.append(episode)
        return eps
