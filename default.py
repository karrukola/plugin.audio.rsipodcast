"""
Main module of Kodi (XBMC) addon to manage RSI.ch podcast section.

This is the main module that takes care of receiving the information from the
parser and present it in Kodi creating the appropriate pages and feeding the
URL of the media content to the player.
"""

import os
import sys
import urllib
import urlparse
import xbmcaddon
import xbmcgui
import xbmcplugin

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
addon_handle = int(sys.argv[1])

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)


url_hdcd = 'http://mediaww.rsi.ch/rsi/unrestricted/2016/06/13/2139211.mp3?content-disposition-attachment'

if __name__ == '__main__':
    if mode is None:
        li = xbmcgui.ListItem(label='pippo')
        li.setProperty('IsPlayable', 'true')
        url = build_url({'mode': 'stream', 'url': url_hdcd, 'title': 'pippo'})
        xbmcplugin.addDirectoryItem(handle=addon_handle,
                                        url=url,
                                        listitem=li) 	
        xbmcplugin.endOfDirectory(addon_handle)


    elif mode[0] == 'stream':
        urllalla = args['url'][0]
        play_item = xbmcgui.ListItem(path=urllalla)
        print 'url'
        print urllalla
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
        xbmcplugin.endOfDirectory(addon_handle)
