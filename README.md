# plugin.audio.rsipodcast
A Kodi plugin to surf through RSI podcasts. It all started with my appreciation for Federico Buffa's pieces, together with Angelo Caruso: *Characters*, *London Calling*, *When we were kings*...


## Showcase
### List of stations
![RSI list of stations](https://drive.google.com/open?id=0B_RiBu67K5bGR2FBUTIxUzdqZUU)
![Kodi list of stations](https://drive.google.com/open?id=0B_RiBu67K5bGdHhVR2ZoYmtrOE0)
![Kodi list of stations](https://lh4.googleusercontent.com/027yI5M-gE8K5EUPYauDjGnmuss1a3da6lYiVax2fSaC7_CyKzEF1C_oJfBK4d0s-9bMH2HO8Ucp044=w1920-h940-rw)


## Technicalities
The json APIs of RSI play are used, this to avoid making uncached calls to the servers. 

### RSI APIs
* List of assets for a specific radio station - http://il.srgssr.ch/integrationlayer/1.0/ue/rsi/radio/assetGroup/editorialPlayerAlphabeticalByChannel/rete-tre.json
* List of episoded of a specific show - http://il.srgssr.ch/integrationlayer/1.0/ue/rsi/assetSet/listByAssetGroup/3703891.json
  * go through the list: `?pageNumber=3`
* Episode's details - http://il.srgssr.ch/integrationlayer/1.0/ue/rsi/audio/play/8092102.json

### Image scaling server
* Thumb - EPISODE_IMAGE
* FanARt - WEBVISUAL
I.e. http://www.rsi.ch/rsi-api/resize/image/EPISODE_IMAGE/5644198/
