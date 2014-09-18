#!/usr/bin/env python3


import os.path
from argparse import ArgumentParser
from urllib import request
from hashlib import md5

from bs4 import BeautifulSoup
from progressbar import ProgressBar, Bar, ReverseBar, ETA


def split(input, size):
    return [input[start:start+size] for start in range(0, len(input), size)]

def show_progress(pbar, dd, dt):
    if dd >= dt: pass

    pbar.update(dd)


parser = ArgumentParser(description='Fetch Music files from Palco MP3.')
parser.add_argument('url', metavar='URL', type=str,
                    help='Artist page on Palco MP3 to fetch music files')
parser.add_argument('--fnmask', type=str,  default='{number}. {title} - {artist}.mp3',
                    help='File name mask')

args = parser.parse_args()

req = request.urlopen(args.url)

html = req.read()

soup = BeautifulSoup(html)

pl = soup.find(class_="player_playlist")

for music in pl.find_all('li'):
    s = music['data-servidor']
    a = music['data-arquivo']
    number = int(music['data-i']) + 1
    artist = music['data-artista']
    title = music.a.span.string

    e = split(md5(a.encode()).hexdigest(), 1)
    url = "{0}{1}/{2}/{3}/{4}/{5}".format(s, e[0], e[1], e[2], e[3], a)
    # add http:
    if url.startswith('//'):
        url = 'http:' + url

    fname = args.fnmask.format(number=number, title=title, artist=artist)

    # If file already exists just skip it
    if (os.path.isfile(fname)): continue
    with open(fname, 'wb') as mp3:
        resp = request.urlopen(url)
        total_size = int(resp.headers['Content-Length'].strip())

        print(fname)

        widgets = [Bar('>'), ' ', ETA(), ' ', ReverseBar('<')]
        pbar = ProgressBar(widgets=widgets, maxval=total_size).start()
        while True:
            read = resp.read(8192)
            if (not read): break

            mp3.write(read)
            show_progress(pbar, mp3.tell(), total_size)
        pbar.finish()
        print('\n')
