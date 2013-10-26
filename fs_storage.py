
import json
import os


def get_programs(channel):
    db_list = []
    filename = 'db/%s.txt' % channel.name
    try:
        with open(filename, 'r') as infile:
            db_list = json.load(infile)
    except IOError as e:
        print 'no file %s' % filename
    return db_list


def save_programs(channel, prog_list):
    filename = 'db/%s.txt' % channel.name
    with open(filename, 'w') as outfile:
        json.dump(prog_list, outfile)


def get_episodes(program):
    db_list = []
    dirname = 'db/%s_programs' % program['channel']
    filename = '%s/%s.txt' % (dirname, program['id'])
    try:
        with open(filename, 'r') as infile:
            db_list = json.load(infile)
    except IOError as e:
        print 'no file %s' % filename
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
    return db_list


def save_episodes(program, episode_list):
    filename = 'db/%s_programs/%s.txt' % (program['channel'], program['id'])
    with open(filename, 'w') as outfile:
        json.dump(episode_list, outfile)
