__author__ = 'coop'

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import os
import sys


def notify(addonId, message, timeShown=5000):
    """Displays a notification to the user

    Parameters:
    addonId: the current addon id
    message: the message to be shown
    timeShown: the length of time for which the notification will be shown, in milliseconds, 5 seconds by default
    """
    addon = xbmcaddon.Addon(addonId)
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (addon.getAddonInfo('name'), message, timeShown, addon.getAddonInfo('icon')))


def show_error(addonId, errorMessage):
    """
    Shows an error to the user and logs it

    Parameters:
    addonId: the current addon id
    message: the message to be shown
    """
    notify(addonId, errorMessage)
    xbmc.log(errorMessage, xbmc.LOGERROR)


def die(rc, message):
    """print message and exit"""
    xbmc.log(message)
    sys.exit(rc)


def make_link(params, base_url=sys.argv[0]):
    """
    Build a link with the specified base URL and parameters

    Parameters:
    params: the params to be added to the URL
    BaseURL: the base URL, sys.argv[0] by default
    """
    import urllib
    url = urllib.urlencode(dict([k.encode('utf-8'),unicode(v).encode('utf-8')] for k,v in params.items()))
    return base_url + '?' + url


def add_menu_item(caption, link, icon=None, thumbnail=None, folder=False):
    """
    Add a menu item to the xbmc GUI

    Parameters:
    caption: the caption for the menu item
    icon: the icon for the menu item, displayed if the thumbnail is not accessible
    thumbail: the thumbnail for the menu item
    link: the link for the menu item
    folder: True if the menu item is a folder, false if it is a terminal menu item

    Returns True if the item is successfully added, False otherwise
    """
    listItem = xbmcgui.ListItem(unicode(caption), iconImage=icon, thumbnailImage=thumbnail)
    listItem.setInfo(type="Video", infoLabels={ "Title": caption })
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=listItem, isFolder=folder)

def end_listing():
    """
    Signals the end of the menu listing
    """
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def parse_parameters(input_string=sys.argv[2]):
    """Parses a parameter string starting at the first ? found in inputString

    Argument:
    inputString: the string to be parsed, sys.argv[2] by default

    Returns a dictionary with parameter names as keys and parameter values as values
    """
    import urlparse
    parameters = {}
    for name, value in urlparse.parse_qsl(input_string, 0, 0):
        parameters[name] = value

    return parameters


def get_user_input(heading, hidden=False):
    # Create the keyboard object and display it modal
    oKeyboard = xbmc.Keyboard('', heading, hidden)
    oKeyboard.doModal()
    # If key board is confirmed and there was text entered return the text
    if oKeyboard.isConfirmed():
      sSearchText = oKeyboard.getText()
      if len(sSearchText) > 0:
        return sSearchText
    return False
