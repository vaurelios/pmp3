#!/usr/bin/env python3


import os.path
import json
import sys
from argparse import ArgumentParser
from urllib import request
from hashlib import md5

from progressbar import ProgressBar, Bar, ReverseBar, ETA

# API urls
API_URL_INFO = 'http://api.palcomp3.com/v1/artists/{artist}/info.json'
API_URL_ARTIST = 'http://api.palcomp3.com/v1/artists/{artist}/songs.json'
API_URL_GENERES = 'http://api.palcomp3.com/v1/generos/todos.json'


class RemoteFile:
    def __init__(self):
        self.url = ''
        self.dest_name = ''
        self.fnmask = ''
        self.track_number = 0
        self.title = ''
        self.artist = ''
        self.data = object()

    def __ssplit(self, input, size):
        return [input[start:start+size] for start in range(0, len(input), size)]

    def pull_data(self):
        h = self.__ssplit(md5(self.data['arquivo'].encode()).hexdigest(), 1)
        self.url ="{0}{1}/{2}/{3}/{4}/{5}".format(self.data['servidor'], h[0], h[1], h[2], h[3], self.data['arquivo'])

        if self.url.startswith('//'):
            self.url = 'http:' + self.url

        self.track_number = int(self.data['ordem']) + 1
        self.title = self.data['titulo']

        self.dest_name = self.fnmask.format(number=self.track_number, artist=self.artist, title=self.title)


class PMP3:
    def __init__(self):
        self.__count = 1
        self.musics = []

    def __update_progress(self, dd, dt):
        if dd >= dt: pass

        self.pbar.update(dd)

    def __sprint(self, ln):
        sys.stdout.write(ln)
        sys.stdout.flush()

    def parse_args(self):
        parser = ArgumentParser(description='Fetch Music files from Palco MP3.')
        parser.add_argument('artistid', metavar='Artist ID', type=str,
                    help='Artist ID on Palco MP3 to fetch music files')
        parser.add_argument('--fnmask', type=str,  default='{number}. {title} - {artist}.mp3',
                    help='File name mask')
        parser.add_argument('--write-id3', action='store_true', help='Write ID3 Metadata to files (may override)')

        self.args = parser.parse_args()

    def fetch_songs(self):
        req = request.urlopen(API_URL_ARTIST.format(artist=self.args.artistid))

        self.songs = json.loads(req.read().decode('UTF-8'))

    def fetch_info(self):
        req = request.urlopen(API_URL_INFO.format(artist=self.args.artistid))

        self.info = json.loads(req.read().decode('UTF-8'))[0]

    def build_music_list(self):
        for data in self.songs:
            music = RemoteFile()
            music.artist = self.info['nome']
            music.data = data
            music.fnmask = self.args.fnmask
            music.pull_data()
            self.musics.append(music)

    def fetch_generes(self):
        req = request.urlopen(API_URL_GENERES)

        self.generes = {}

    def do_download(self):
        self.__sprint("Fetching artist info...")
        self.fetch_info()
        self.__sprint(" done\n")
        self.__sprint("Fetching song info...")
        self.fetch_songs()
        self.__sprint(" done\n")
        self.build_music_list()

        for music in self.musics:
            if (os.path.isfile(music.dest_name)): continue
            with open(music.dest_name, 'wb') as mp3:
                resp = request.urlopen(music.url)
                total_size = int(resp.headers['Content-Length'].strip())

                print(music.dest_name)

                widgets = [Bar('>'), ' ', ETA(), ' ', ReverseBar('<')]
                self.pbar = ProgressBar(widgets=widgets, maxval=total_size).start()

                while True:
                    read = resp.read(8192)
                    if (not read): break

                    mp3.write(read)
                    self.__update_progress(mp3.tell(), total_size)
                self.pbar.finish()
                self.__sprint('\n')


if __name__ == '__main__':
    pmp3 = PMP3()
    pmp3.parse_args()
    pmp3.do_download()

