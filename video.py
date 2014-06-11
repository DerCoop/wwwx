__author__ = 'coop'

import xbmcgui
import xbmc
import os


class WwwxPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)

    def set_stuff(self, pid, link):
        self.pid = pid
        self.link = link


    #def onPlayBackEnded(self):
    #    self.__teardown__()

    #def onPlayBackStopped(self):
    #    self.__teardown__()

    #def stop(self):
    #    self.__teardown__()

    def __teardown__(self):
        print 'will kill ', self.pid
        try:
            os.kill(self.pid, 9)
        except:
            pass

        try:
            os.unlink(self.link)
        except:
            pass


def play(title, thumbnail, link, mediaType='Video', pid=0):
    """Plays a video

    Arguments:
    title: the title to be displayed
    thumbnail: the thumnail to be used as an icon and thumbnail
    link: the link to the media to be played
    mediaType: the type of media to play, defaults to Video. Known values are Video, Pictures, Music and Programs
    """
    li = xbmcgui.ListItem(label=title, iconImage=thumbnail, thumbnailImage=thumbnail, path=link)
    li.setInfo(type=mediaType, infoLabels={"Title": title})
    player = WwwxPlayer()
    player.set_stuff(pid, link)
    player.play(item=link, listitem=li)
