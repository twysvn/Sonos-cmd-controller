#!/usr/bin/env python3
from soco import SoCo
import soco
import time
import sys
from random import randint
import requests
from pprint import pprint
import json
import re
import os

debug = True

yellow = "\033[33m"
normal = "\033[0;33;0m"
grey = "\033[90m"

try:
    columns, rows = os.get_terminal_size(0)
except OSError:
    columns, rows = os.get_terminal_size(1)

def help():
    print("Sonos")
    print("sonos cmd [args]")
    print("args := (i)nfo, (n)ext, (pr)evious, (pl)ay, (p)ause, (s)huffle, (v)olume [0-100], (q)ueue [index], (r)andom, (r)e(m)ove, playlist/add, (l)yrics [restart?], (s)ee(k)")


def info():
    track = sonos.get_current_track_info()
    print (int(track["playlist_position"]) - 1, yellow + track["title"]+normal, "-", track["artist"], "", "(",track["album"],")")

def queue():
    track = sonos.get_current_track_info()
    index = int(track["playlist_position"])-1

    pi = min(10, int((rows-4)/3))
    queue = sonos.get_queue(start=max(index - pi, 0), max_items=rows-4)

    i = max(index-pi, 0)
    maxlen = len(str(i + len(queue)))
    for track in queue:
        if i > len(queue) + index:
            break
        title = "🥚🥚"
        creator = "🥚🥚"
        if hasattr(track, 'title'):
            title = track.title
        if hasattr(track, 'creator'):
            creator = track.creator
        if i == index:
            print(grey + "-"*columns + normal)
            track = sonos.get_current_track_info()
            pos = track["position"].split(":")
            dur = track["duration"].split(":")
            pos = int(int(pos[0])*60*60+int(pos[1])*60+int(pos[2]))
            dur = int(int(dur[0])*60*60+int(dur[1])*60+int(dur[2]))
            # bar_len = 147
            bar_len = columns - 34
            w = int(bar_len*pos/dur)
            print (int(track["playlist_position"]) - 1, yellow + track["title"]+normal, track["artist"], "", grey+"(",track["album"],")"+normal)
            print("Volume:", str(sonos.volume).rjust(3) + "%", "|", track["position"], "["+("="*w)+">" + " "*(bar_len-w)+"]", track["duration"])
            print(grey + "-"*columns + normal)
        else:
            print (str(i).ljust(maxlen), grey+title+normal, creator)
        i += 1

def children(json):
    t = type(json)
    if type(json) is str:
        return json
    elif t is list:
        s = ""
        for i in json:
            g = children(i)
            if g:
                s += children(i)
        return s
    elif t is dict:
        s = ""
        for key, value in json.items():
            if key == "children":
                s += children(value)
            elif key == "tag" and value == "br":
                s += "\n"
        return s
    return ""

def print_lyrics(jsn):

    if debug:
        with open("lyrics.json", "w") as f:
            f.write(json.dumps(jsn))
            f.close()

    jsn = jsn["dom"]["children"]
    for d in jsn:
        print(children(d))

if __name__ == '__main__':
    sonos = list(soco.discover())

    if len(sonos) == 0:
        print("sonos not found")
        sys.exit(0)

    sonos = sonos[0]

    if len(sys.argv) < 2:
        help()
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "help"          or cmd == "?" or cmd == "h" or cmd == "halp" \
                                or cmd == "hälp" or cmd == "yelp" or cmd == "-h" \
                                or cmd == "--help" or cmd == "-?" or cmd == "--?" \
                                or cmd == "what" or cmd == "wat" or cmd == "kek" \
                                or cmd == "lol" or cmd == "is_there_something_that_doesnt_trigger_help" \
                                or cmd == "nah_there_isnt":
        help()
    elif cmd == "info"        or cmd == "i":
        queue()
    elif cmd == "next"        or cmd == "n":
        if len(sys.argv) == 3:
            for i in range(int(sys.argv[2])):
                sonos.next()
                time.sleep(0.1)
        else:
            sonos.next()
        queue()
    elif cmd == "previous"    or cmd == "pr":
        sonos.previous()
        queue()
    elif cmd == "play"        or cmd == "pl":
        sonos.play()
        queue()
    elif cmd == "pause"       or cmd == "p":
        sonos.pause()
    elif cmd == "shuffle"     or cmd == "s":
        sonos.avTransport.SetPlayMode([
            ('InstanceID', 0),
            ('NewPlayMode', "NORMAL")
        ])
        sonos.avTransport.SetPlayMode([
            ('InstanceID', 0),
            ('NewPlayMode', "SHUFFLE")
        ])
        queue()
    elif cmd == "volume"      or cmd == "v":
        if len(sys.argv) == 3:
            if sys.argv[2].startswith("+"):
                n = sonos.volume + 2 * len(sys.argv[2])
                sonos.volume = min(n, 50)
            elif sys.argv[2].startswith("-"):
                sonos.volume -= 2 * len(sys.argv[2])
            elif int(sys.argv[2]) < 51:
                sonos.volume = sys.argv[2]
            else:
                print("haha osch wol gedenkt 8===D")
        queue()


    elif cmd == "queue" or cmd == "q":
        track = sonos.get_current_track_info()
        index = int(track["playlist_position"])-1

        if len(sys.argv) == 3:
            index = min(int(sys.argv[2]), sonos.queue_size - 1)
            sonos.play_from_queue(index)
        queue()

    elif cmd == "random" or cmd == "r":
        size = sonos.queue_size
        rand = randint(0, size-1)
        sonos.play_from_queue(rand)
        queue()

    elif cmd == "remove" or cmd == "rm":
        if len(sys.argv) == 3:
            sonos.remove_from_queue(int(sys.argv[2]))
        else:
            track = sonos.get_current_track_info()
            index = int(track["playlist_position"])-1
            sonos.remove_from_queue(index)
        queue()

    elif cmd == "playlist" or cmd == "add":
        if len(sys.argv) == 3:
            playlist = sonos.get_sonos_playlist_by_attr('title', sys.argv[2])

            index = int(sonos.get_current_track_info()["playlist_position"]) - 1
            item = sonos.get_queue(start=index, max_items=1)[0]

            sonos.add_item_to_sonos_playlist(item, playlist)
        else:
            plists = list(sonos.get_sonos_playlists())
            for plist in plists:
                print(plist.title)

    elif cmd == "lyrics" or cmd == "l":

        if len(sys.argv) > 2:
            sonos.seek("00:00:00")

        track = sonos.get_current_track_info()
        artist = re.sub("\(.*?\)|\[.*?\]|", "", track["artist"])
        title = re.sub("\(.*?\)|\[.*?\]|", "", track["title"])
        query = artist+" "+title
        query.replace(" ", "%20")

        s = requests.Session()
        res = s.get("https://api.genius.com/home/ios", headers={
            "User-Agent":"Genius/com.rapgenius.RapGenius (5.5.1 (Build 697); iOS Version 12.1.1 (Build 16C50))",
            "X-Genius-iOS-Version":"5.5.1"
        })
        # print(res.status_code, res.content)
        res = s.get("https://api.genius.com/apple_tokens/IT", headers={
            "User-Agent":"Genius/com.rapgenius.RapGenius (5.5.1 (Build 697); iOS Version 12.1.1 (Build 16C50))",
            "X-Genius-iOS-Version":"5.5.1"
        })
        # print(res.status_code, res.content)
        res = s.get("https://api.genius.com/search/multi?q="+query+"&per_page=3", headers={
            "User-Agent":"Genius/com.rapgenius.RapGenius (5.5.1 (Build 697); iOS Version 12.1.1 (Build 16C50))",
            "X-Genius-iOS-Version":"5.5.1"
        })
        hits = json.loads(res.content)["response"]["sections"][0]["hits"]
        if len(hits) < 1:
            print("no lyrics found")
            sys.exit(0)
        path = hits[0]["result"]["api_path"]
        res = s.get("https://api.genius.com"+path, headers={
            "User-Agent":"Genius/com.rapgenius.RapGenius (5.5.1 (Build 697); iOS Version 12.1.1 (Build 16C50))",
            "X-Genius-iOS-Version":"5.5.1"
        })
        print()
        print(yellow+json.loads(res.content)["response"]["song"]["full_title"]+normal)
        print()
        print_lyrics(json.loads(res.content)["response"]["song"]["lyrics"])

    elif cmd == "seek" or cmd == "sk":
        if len(sys.argv) == 3:
            sonos.seek(sys.argv[2])
            queue()
        else:
            print("use HH:MM:SS")
    else:
        queue()
