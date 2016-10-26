import os
import sys
import urllib
import urlparse
import xbmcaddon
import xbmcgui
import xbmcplugin
from json import loads
import requests

BASEURL = 'http://il.srgssr.ch/integrationlayer/1.0/ue/rsi/'

CHLIST = [
    ('rete-uno',
     'http://www.rsi.ch/play/assets/img/srg/rsi/rete_uno_wide.png'),
    ('rete-due',
     'http://www.rsi.ch/play/assets/img/srg/rsi/rete_due_wide.png'),
    ('rete-tre',
     'http://www.rsi.ch/play/assets/img/srg/rsi/rete_tre_wide.png')
]


def build_url(query):
    """
    Kodi passess paramteres through a URL that is used to call the plugin itself
    """
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)


def get_shows(channelid):
    """
    Return a json object with all the shows for a certain channel
    """
    url = BASEURL + 'radio/assetGroup/editorialPlayerAlphabeticalByChannel/' + \
            channelid + '.json'
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
    resp = requests.get(url=url)
    data = loads(resp.text)
    return data['Audio']['Playlists']['Playlist'][0]['url'][0]['text']


def play_episode(episodeId, addon_handle):
    """
    Play the selected episode
    """
    epUrl = get_episode_audio_url(episodeId)
    li = xbmcgui.ListItem(path=epUrl)
    xbmcplugin.setResolvedUrl(addon_handle, True, li)
    return epUrl


def add_show(show, addon_handle):
    """
    Add a list item for each show
    """
    try:
        thumb = show['Image']['ImageRepresentations']['ImageRepresentation'][0]['url']
    except:
        thumb = None

    li = xbmcgui.ListItem(label=show['title'].encode('utf-8').strip(),
                          thumbnailImage=thumb)
    xbmcplugin.addDirectoryItem(handle=addon_handle,
                                url=build_url({'mode': 'AssetGroup',
                                               'rsiid': show['id']}),
                                listitem=li,
                                isFolder=True)
    return


def add_episode(ep, addon_handle):
    """
    Add a list item for each episode
    """
    try:
        thumb = ep['Assets']['Image']['ImageRepresentations']['ImageRepresentation'][0]['url']
    except:
        thumb = None
    li = xbmcgui.ListItem(label=ep['title'].encode('utf-8').strip(),
                          thumbnailImage=thumb)
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=addon_handle,
                                url=build_url({'mode': 'play',
                                               'rsiid': ep['id']}),
                                listitem=li)
    return


def main():
    """
    main function, handles modes and lists creation in Kodi
    """
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    rsiid = args.get('rsiid', None)
    if mode is None:
        # create list of (radio) channels
        for channel in CHLIST:
            li = xbmcgui.ListItem(label=channel[0],
                                  thumbnailImage=channel[1])
            xbmcplugin.addDirectoryItem(handle=addon_handle,
                                        url=build_url({'mode': 'channel', 'rsiid': channel[0]}),
                                        listitem=li,
                                        isFolder=True)
    elif mode[0] == 'channel':
        showsList = get_shows(rsiid[0])
        for show in showsList:
            add_show(show, addon_handle)
    elif mode[0] == 'AssetGroup':
        episodesList = get_episodes(rsiid[0])
        for episode in episodesList:
            add_episode(episode, addon_handle)
    elif mode[0] == 'play':
        play_episode(rsiid[0], addon_handle)

    # e chiudiamo la lista per tutti i modi
    xbmcplugin.endOfDirectory(addon_handle)


if __name__ == '__main__':
    addon_handle = int(sys.argv[1])
    main()
