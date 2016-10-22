import os
import sys
import urllib
import urlparse
import xbmcaddon
import xbmcgui
import xbmcplugin
import requests
from json import loads

BASEURL = 'http://il.srgssr.ch/integrationlayer/1.0/ue/rsi/'


def build_url(query):
    """
    Kodi passess paramteres through a URL that is used to call the plugin itself
    """
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)


def get_shows(channelId):
    """
    Return a json object with all the shows for a certain channel
    """
    url = BASEURL + 'radio/assetGroup/editorialPlayerAlphabeticalByChannel/' + \
        channelId + '.json'
    resp = requests.get(url=url)
    data = loads(resp.text)
    return data['AssetGroups']['Show']


def get_episodes(showId):
    url = BASEURL + 'assetSet/listByAssetGroup/' + showId + '.json'
    resp = requests.get(url=url)
    data = loads(resp.text)
    return data['AssetSets']['AssetSet']


def get_episode_audio_url(episodeId):
    url = BASEURL + 'audio/play/' + episodeId + '.json'
    print url
    resp = requests.get(url=url)
    data = loads(resp.text)
    return data['Audio']['Playlists']['Playlist'][0]['url'][0]['text']


def play_episode(episodeId):
    epUrl = get_episode_audio_url(episodeId)

    return epUrl


def add_show(show):
    print "#####"
    print show['id']
    print show['title'].encode('utf-8').strip()
    try:
        print show['Image']['ImageRepresentations']['ImageRepresentation'][0]['url']
    except:
        print "default image"
    print ""

    return


def add_episode(episode):
    return


def main():
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    if mode is None:
        # # !!!ToDo!!! when mode is None create list of channels. You must find a way to include channels' icons
        # showsList = get_shows('rete-tre')
        # for show in showsList:
        #     add_show(show)

        # episodesList = get_episodes('3703891')
        # for episode in episodesList:
        #     print episode['title'].encode('utf-8').strip()

        epUrl = play_episode('8092102')
        play_item = xbmcgui.ListItem(path=epUrl)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

if __name__ == '__main__':
    # sample_page = BASEURL + 'radio/assetGroup/editorialPlayerAlphabeticalByChannel/rete-tre.json'
    addon_handle = int(sys.argv[1])
    main()
