import os
import sys
from json import loads
import urllib
import urlparse
import requests
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmc

BASEURL = 'http://il.srgssr.ch/integrationlayer/1.0/ue/rsi/'

CHLIST = [
    ('rete-uno',
     'http://www.rsi.ch/play/assets/img/srg/rsi/rete_uno_wide.png',
     'Rete Uno'),
    ('rete-due',
     'http://www.rsi.ch/play/assets/img/srg/rsi/rete_due_wide.png',
     'Rete Due'),
    ('rete-tre',
     'http://www.rsi.ch/play/assets/img/srg/rsi/rete_tre_wide.png',
     'Rete Tre')
]


def build_url(query):
    """To pass the parameters among plugin calls
    """
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)


def gen_image_url(imgid, usage):
    """Generata image url based on its id and usage
    Possible values for usage:
    WEBVISUAL (980x550)
    EPISODE_IMAGE (624x351)
    """
    if imgid is not None:
        xbmc.log('imgid is not None')
        return 'http://www.rsi.ch/rsi-api/resize/image/' + usage + '/' + imgid + '/'
    elif imgid == 'None':
        xbmc.log('imgid is None (string)')
        return None
    else:
        xbmc.log('imgid is None')
        return None

def get_az_shows(channelid):
    """Return a json object with all the shows for a certain channel
    """
    url = BASEURL + 'radio/assetGroup/editorialPlayerAlphabeticalByChannel/' + channelid + '.json'
    resp = requests.get(url=url)
    data = loads(resp.text)
    return data['AssetGroups']['Show']


def get_episodes(showid, scope, page, maxeps):
    """Get episodes list for a given ID.
    Episodes are paginated in groups of 10, thus you need to know the page
    """
    if scope == 'AssetGroup':
        url = BASEURL + 'assetSet/listByAssetGroup/' + showid + '.json'
        if page is not None:
            url += '?pageNumber=' + page[0]
    elif scope == 'mostRecent':
        url = BASEURL + 'audio/editorialPlayerLatestByChannel/'
        url += showid + '.json?pageSize=' + str(maxeps)
    elif scope == 'mostClicked':
        url = BASEURL + 'audio/mostClickedByChannel/'
        url += showid + '.json?pageSize=' + str(maxeps)
    else:
        raise NameError('rsi')
    print url
    resp = requests.get(url=url)
    data = loads(resp.text)
    if scope == 'AssetGroup':
        episodeslist = data['AssetSets']['AssetSet']
        pagesize = data['AssetSets']['@pageSize']
    else:
        episodeslist = data['Audios']['Audio']
        pagesize = data['Audios']['@pageSize']
    return episodeslist, pagesize


def get_episode_details(episodeid):
    """Retrieve the mp3 URL
    """
    url = BASEURL + 'audio/play/' + episodeid + '.json'
    resp = requests.get(url=url)
    return loads(resp.text)


def play_episode(episodeid):
    """Play the selected episode
    """
    data = get_episode_details(episodeid)
    audio_url = data['Audio']['Playlists']['Playlist'][0]['url'][0]['text']
    kli = xbmcgui.ListItem(path=audio_url)
    kli.setInfo('music', {'title': data['Audio']['AssetSet']['title'].encode('utf-8').strip(),
                          'album': data['Audio']['AssetSet']['Show']['title'].encode('utf-8').strip(),
                          'artist': data['Audio']['AssetSet']['Show']['lead'].encode('utf-8').strip(),
                          'date': data['Audio']['modifiedDate']})
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, kli)
    return


def add_show(show):
    """Add a list item for each show
    """
    try:
        imgid = show['Image']['ImageRepresentations']['ImageRepresentation'][0]['id']
        thumb = gen_image_url(imgid, 'EPISODE_IMAGE')
    except:
        imgid = None
        thumb = None

    kli = xbmcgui.ListItem(label=show['title'].encode('utf-8').strip())
    if thumb is not None:
        kli.setArt({'thumb': thumb})
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE,
                                url=build_url({'mode': 'AssetGroup',
                                               'rsiid': show['id'],
                                               'imgid': imgid}),
                                listitem=kli,
                                isFolder=True)
    return


def add_episode(epdata, fanart_url, scope):
    """Add a list item for each episode
    """
    if scope == 'AssetGroup':
        kli = xbmcgui.ListItem(label=epdata['title'].encode('utf-8').strip())
    else:
        kli = xbmcgui.ListItem(label=epdata['AssetSet']['title'].encode('utf-8').strip())
        fanart_url = epdata['Image']['ImageRepresentations']['ImageRepresentation'][0]['url']
    kli.setProperty('IsPlayable', 'true')
    if fanart_url is not None:
        kli.setArt({'fanart': fanart_url})
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE,
                                url=build_url({'mode': 'play',
                                               'rsiid': epdata['id']}),
                                listitem=kli)
    return


def add_next_page(page, rsiid, imgid):
    """Add navigation to another page
    """
    if page is None:
        nextpage = 2
    else:
        nextpage = int(page[0]) + 1
    kli = xbmcgui.ListItem(label=">>> Mostra di piu [" + str(nextpage) + "] >>>")
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE,
                                url=build_url({'mode': 'AssetGroup',
                                               'rsiid': rsiid[0],
                                               'page': str(nextpage),
                                               'imgid': imgid}),
                                listitem=kli,
                                isFolder=True)
    return


def add_episodes(rsiid, scope, imgid, page, maxeps=None):
    """This adds a number of episodes to the list.
    This number is a parameter so you can tweak pagination in Kodi"""
    fanart_url = gen_image_url(imgid, 'WEBVISUAL')
    episodeslist, pagesize = get_episodes(rsiid[0], scope, page, maxeps)
    for i, episode in enumerate(episodeslist):
        if maxeps is not None and i >= maxeps:
            break
        else:
            add_episode(episode, fanart_url, scope)
    if maxeps is None and pagesize != 0:
        add_next_page(page, rsiid, imgid)
    return


def main():
    """main function, handles modes and lists creation in Kodi
    """
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    rsiid = args.get('rsiid', None)
    page = args.get('page', None)
    imgid = args.get('imgid', None)
    if mode is None:
        # create list of (radio) channels
        for channel in CHLIST:
            kli = xbmcgui.ListItem(label=channel[2],
                                   thumbnailImage=channel[1])
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE,
                                        url=build_url({'mode': 'channel',
                                                       'rsiid': channel[0]}),
                                        listitem=kli,
                                        isFolder=True)
    elif mode[0] == 'channel':
        """Le ultime 24 ore
        i.e. http://il.srgssr.ch/integrationlayer/1.0/ue/rsi/audio/
              editorialPlayerLatestByChannel/rete-tre.json?pageSize=20
        I piu ascoltati
        i.e. http://il.srgssr.ch/integrationlayer/1.0/ue/rsi/audio/
              mostClickedByChannel/rete-tre.json?pageSize=20
        Trasmissioni dalla A alla Z"""
        add_episodes(rsiid, 'mostRecent', imgid, page, 4)
        add_episodes(rsiid, 'mostClicked', imgid, page, 5)
        showslist = get_az_shows(rsiid[0])
        for show in showslist:
            add_show(show)
    elif mode[0] == 'AssetGroup':  # AssetGroup - List of episodes
        if imgid is not None:
            imgid = imgid[0]
        add_episodes(rsiid, 'AssetGroup', imgid, page)
    elif mode[0] == 'play':
        play_episode(rsiid[0])
    # e chiudiamo la lista per tutti i modi
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


if __name__ == '__main__':
    ADDON_HANDLE = int(sys.argv[1])
    main()
