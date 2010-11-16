#!/usr/bin/evn python

import sys
import os
import time
from datetime import datetime
import json

import lastfm
import lastfm.error

import web

def get_lastfm_handler():
    api_key = 'hello api key'
    handler = lastfm.Api(api_key, no_cache=True,
                         request_headers = {'Cache-Control' : 'max-age=5'})
    return handler

def ndays(n, tracks):
    today = datetime.now()
    for track in tracks:
        age = today - track.played_on
        if age.days < n:
            yield age.days, track
        else:
            return

def get_daily_counts(days, tracks):
    today = datetime.now()
    result = [0] * days
    for age, track in ndays(days, tracks):
        result[age] += 1
    return result
    
class RecentPlaycountsRPC:
    def GET(self):
        handler = get_lastfm_handler()
        username = web.input(user='jcinfo').user
        user = None
        counts = [0]
        try:
            user = lastfm.user.User(handler, name=username, bypass_registry=True)
            counts = get_daily_counts(30, user.get_recent_tracks(limit=50))
        except lastfm.error.InvalidParametersError:
            pass
        lsdata = ",".join("%s" % i for i in counts)
        ls = "".join(("http://chart.apis.google.com/chart?",
                     "chs=250x50&cht=lc:nda",
                     "&chls=4,1,0",
                     "&chma=0,0,0,0",
                     "&chco=FF8000",
                     "&chf=bg,s,878787",
                     "&chm=B,999999,0,0,0",
                      "&chd=t:0,%s,0" % lsdata))
        return json.dumps(ls)

class NowPlayingRPC:
    def GET(self):
        handler = get_lastfm_handler()
        result = {}
        username = web.input(user='jcinfo').user
        user = lastfm.user.User(handler, name=username, bypass_registry=True)
        tracks = user.get_recent_tracks(limit=10)
        for i, track in enumerate(tracks):
            if i > 5:
                break
        track = user.now_playing
        if track:
            if track.image['extralarge']:
                result['image'] =  track.image['extralarge']
            elif track.artist.image['extralarge']:
                result['image'] = track.artist.image['extralarge']
            result['artist'] = track.artist.name
            result['artisturl'] = track.artist.url
            result['track'] = track.name
            result['trackurl'] = track.url
            result['stopped'] = False
        else:
            result['stopped'] = True
        return json.dumps(result)
                
        
class NowPlayingPage:
    def GET(self, username):
        handler = get_lastfm_handler()
        if username == "" or username is None:
            username = "jcinfo"
        user = None
        try:
            user = handler.get_user(username)
        except lastfm.error.InvalidParametersError:
            return "Unknown user %s" % username

        template_root = os.path.join(os.path.dirname(__file__), "templates") 
        render = web.template.render(template_root)
        return render.playing(user)

def main():
    urls = ("/now_playing", "NowPlayingRPC",
            "/play_chart", "RecentPlaycountsRPC",
            "/(.*)", "NowPlayingPage")
    app = web.application(urls, globals())
    return app

application = main().wsgifunc()

if __name__ == "__main__":
    main().run()

