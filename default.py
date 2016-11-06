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
    To pass the parameters among plugin calls
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


def get_episodes(showid, page):
    """
    Get episodes list for a given ID.
    Episodes are paginated in groups of 10, thus you need to know the page
    """
    url = BASEURL + 'assetSet/listByAssetGroup/' + showid + '.json'
    if page is not None:
        url += '?pageNumber=' + page[0]
    resp = requests.get(url=url)
    data = loads(resp.text)
    episodeslist = data['AssetSets']['AssetSet']
    pagesize = data['AssetSets']['@pageSize']
    return episodeslist, pagesize


def get_episode_details(episodeid):
    """
    Retrieve the mp3 URL
    """
    url = BASEURL + 'audio/play/' + episodeid + '.json'
    resp = requests.get(url=url)
    return loads(resp.text)


def play_episode(episodeId):
    """
    Play the selected episode
    """
    data = get_episode_details(episodeId)
    audio_url = data['Audio']['Playlists']['Playlist'][0]['url'][0]['text']
    kli = xbmcgui.ListItem(path=audio_url)
    kli.setInfo('music', {'title': data['Audio']['AssetSet']['title'].encode('utf-8').strip(),
                          'album': data['Audio']['AssetSet']['Show']['title'].encode('utf-8').strip(),
                          'artist': data['Audio']['AssetSet']['Show']['lead'].encode('utf-8').strip(),
                          'date': data['Audio']['modifiedDate']})
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, kli)
    return


def add_show(show):
    """
    Add a list item for each show
    """
    try:
        thumb = show['Image']['ImageRepresentations']['ImageRepresentation'][0]['url']
    except:
        thumb = None

    kli = xbmcgui.ListItem(label=show['title'].encode('utf-8').strip(),
                           thumbnailImage=thumb)
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE,
                                url=build_url({'mode': 'AssetGroup',
                                               'rsiid': show['id']}),
                                listitem=kli,
                                isFolder=True)
    return


def add_episode(ep):
    """
    Add a list item for each episode
    """
    try:
        thumb = ep['Assets']['Image']['ImageRepresentations']['ImageRepresentation'][0]['url']
    except:
        thumb = None
    kli = xbmcgui.ListItem(label=ep['title'].encode('utf-8').strip(),
                           thumbnailImage=thumb)
    kli.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE,
                                url=build_url({'mode': 'play',
                                               'rsiid': ep['id']}),
                                listitem=kli)
    return


def add_next_page(page, rsiid):
    """
    Add navigation to another page
    """
    if page is None:
        nextpage = 2
    else:
        nextpage = int(page[0]) + 1
    kli = xbmcgui.ListItem(label=">>> Mostra di piu [" + str(nextpage) + "] >>>")
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE,
                                url=build_url({'mode': 'AssetGroup',
                                               'rsiid': rsiid[0],
                                               'page': str(nextpage)}),
                                listitem=kli,
                                isFolder=True)
    return


def main():
    """
    main function, handles modes and lists creation in Kodi
    """
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    rsiid = args.get('rsiid', None)
    page = args.get('page', None)
    if mode is None:
        # create list of (radio) channels
        for channel in CHLIST:
            kli = xbmcgui.ListItem(label=channel[0],
                                   thumbnailImage=channel[1])
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE,
                                        url=build_url({'mode': 'channel', 'rsiid': channel[0]}),
                                        listitem=kli,
                                        isFolder=True)
    elif mode[0] == 'channel':
        showslist = get_shows(rsiid[0])
        for show in showslist:
            add_show(show)
    elif mode[0] == 'AssetGroup':
        episodeslist, pagesize = get_episodes(rsiid[0], page)
        for episode in episodeslist:
            add_episode(episode)
        if pagesize != 0:
            add_next_page(page, rsiid)
    elif mode[0] == 'play':
        play_episode(rsiid[0])

    # e chiudiamo la lista per tutti i modi
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


if __name__ == '__main__':
    ADDON_HANDLE = int(sys.argv[1])
    main()
