#!/usr/bin/env python3

 
from urllib import request
from bs4 import BeautifulSoup
from hashlib import md5


def split(input, size):
  return [input[start:start+size] for start in range(0, len(input), size)]


URL = "http://palcomp3.com/bandapressaohits/"

req = request.urlopen(URL)

html = req.read()

soup = BeautifulSoup(html)

pl = soup.find(class_="player_playlist")

for music in pl.find_all('li'):
  fnmask = "{number}. {title} - {artist}.mp3"

  s = music['data-servidor']
  a = music['data-arquivo']
  number = int(music['data-i']) + 1
  artist = music['data-artista']
  title = music.a.span.string

  e = split(md5(a.encode()).hexdigest(), 1)
  url = "{0}{1}/{2}/{3}/{4}/{5}\n".format(s, e[0], e[1], e[2], e[3], a)
  fname = fnmask.format(number=number, title=title, artist=artist)
  
  with open(fname, 'wb') as mp3:
    mp3.write(request.urlopen(url).read())
