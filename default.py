__author__ = 'coop'

import xbmcaddon
from wwwc import config
from wwwc import channelhandler
import os
import misc

addon = xbmcaddon.Addon('plugin.video.wwwx')
localize = addon.getLocalizedString

def cleanup_tmpdir(tmppath):
    import shutil

    for root, dirs, files in os.walk(tmppath):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def get_uid(configfile, session):
    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read(configfile)
    try:
        user_id = config.get('userdata', 'user_id')
        # check user ID
    except:
        import getpass
        from wwwc.sessionhandler import get_user_data
        # ask for the username and password
        username = misc.get_user_input('username')
        passwd = misc.get_user_input('passwd', hidden=True)
        user_id = get_user_data(username, passwd, session)
        if not user_id:
            misc.die(-1, 'unknown user ID')
    return user_id


def play_tv(params, tmppath):
    import xbmcgui
    import subprocess
    import stat
    import xbmc
    import video
    # make cmd
    cmd = ['/storage/.xbmc/addons/plugin.video.wwwx/watch_wilmaa',
           '--config-file', params.get('config_file', ''),
           '--loglevel', 'notset']
    cmd.append('--channel')
    cmd.append(str(params.get('channel', '')))
    fifo = params.get('stream_file')
    try:
        os.remove(fifo)
    except:
        pass
    print cmd
    wilmaa = subprocess.Popen(cmd)
    # store pid in file
    wilmaa_pid_file = os.path.join('/tmp', 'watch_wilmaa.pid')
    with open(wilmaa_pid_file, 'w') as pid_file:
        pid_file.write(str(wilmaa.pid))

    # attention: atomar operations
    # TODO add abort handling
    dialog = xbmcgui.DialogProgress()
    dialog.create("Loading stream...")
    percent = 0
    while not os.path.exists(fifo) or not stat.S_ISFIFO(os.stat(fifo).st_mode):
        dialog.update(percent)
        xbmc.sleep(2000)
        if dialog.iscanceled():
            wilmaa.terminate()
            misc.die(0, 'canceled by user')
        percent += 2
    dialog.update(100)
    #misc.notify('plugin.video.wwwx', 'prepare stream' + params['title'])
    # sleep or do something until the first packet is at the stream
    dialog.close()
    print 'prepare stream FOR ' + params.get('title', '')
    if not video.play(params.get('title', ''), params.get('image', ''), fifo, 'Video', wilmaa.pid):
        print 'can not prepare stream'


def create_icon_link(channel_id, size='360x120px'):
    base_url = 'http://resources.wilmaa.com/logos/'
    return base_url + size + '/images/' + channel_id + '.png'


def get_channel_caption(channel):
    return channel.get_name()


def get_channel_lang(channel):
    return channel.get_lang()


def build_root_menu():
    #build settings entry
    params = {'settings': 1}
    link = misc.make_link(params)
    misc.add_menu_item('Settings', link, '', '')
    # build dirs
    __folder__ = ['de', 'fr', 'en', 'it']
    __images__ = {'de': 'icons/de.png',
                  'fr': 'icons/fr.png',
                  'en': 'icons/en.png',
                  'it': 'icons/it.png',
                  'all': 'icons/luffys.png'}
    for folder in __folder__:
        params = {'mode': folder}
        params['foldername'] = folder
        link = misc.make_link(params)
        misc.add_menu_item(folder, link, icon=__images__[folder], thumbnail=__images__[folder], folder=True)
    misc.end_listing()


def build_channel_menu(channels, lang):
    for channel_id in channels:
        if not get_channel_lang(channels[channel_id]) == lang and not lang == 'all':
            continue
        params = {'play': 1}
        params['channel'] = get_channel_caption(channels[channel_id])
        #params['link'] = channels[channel_id].get_url()
        params['image'] = create_icon_link(channel_id)
        params['title'] = get_channel_caption(channels[channel_id]) + ' (' + channels[channel_id].get_lang() + ')'
        link = misc.make_link(params)
        misc.add_menu_item(params['title'], link, icon=params['image'], thumbnail=params['image'])
    misc.end_listing()


def check_config():
    language = addon.getSetting('language')
    return True


def write_wilmaa_conf(filename, config):
    with open(filename, 'wb+') as fd:
        config.write(fd)


def make_wwwc_main_config():
    import ConfigParser

    config = ConfigParser.RawConfigParser()
    # write in reverse order
    config.add_section('userdata')
    user_id = addon.getSetting('user_id')
    if not user_id == '':
        config.set('userdata', 'user_id', user_id)

    config.add_section('main')
    config.set('main', 'resolution', addon.getSetting('resolution'))

    tmp_path = addon.getSetting('tmp_path')
    if not tmp_path:
        import tempfile
        tmp_path = tempfile.mkdtemp()
    config.set('main', 'stream_file', os.path.join(tmp_path, 'stream.fifo'))
    config.set('main', 'tmp_path', tmp_path)
    proxy = addon.getSetting('proxy')
    if not proxy == '':
        config.set('main', 'proxy', proxy)
    config.set('main', 'uagent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0]')

    configfile = os.path.join(tmp_path, 'wwwc_config.ini')
    try:
        os.remove(configfile)
    except:
        pass
    write_wilmaa_conf(configfile, config)

    return configfile


def generate_uid_ck(configfile, session):
    # create userID cookie and add it to the config
    from wwwc.sessionhandler import create_uid_cookie
    uid = get_uid(configfile, session)
    addon.setSetting('user_id', uid)
    uid_ck = create_uid_cookie(uid)
    session.add_cookie(uid_ck)


def main():
    configfile = make_wwwc_main_config()

    session = config.create_stream_session(configfile)

    tmppath = session.get('tmp_path')
    if not tmppath:
        import tempfile
        tmppath = tempfile.mkdtemp()

    try:
        os.mkdir(tmppath)
    except:
        pass
    # cleanup the tmpdir
    #cleanup_tmpdir(tmppath)

    session.set('tmp_path', tmppath)

    #parameters = misc.parse_parameters()
    import sys
    import urlparse
    #parameters = urlparse.parse_qs(sys.argv[2][1:])
    #parameters = {}
    #for name, value in urlparse.parse_qsl(sys.argv[2][1:], 0, 0):
    #    parameters[name] = value
    parameters = misc.parse_parameters(sys.argv[2][1:])
    if 'play' in parameters:
        # TODO write pidfile to conf'
        pid_file = os.path.join('/tmp', 'watch_wilmaa.pid')
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as fd:
                pid = int(fd.readline())
            try:
                os.kill(pid, 9)
            except:
                pass
        parameters['config_file'] = configfile
        parameters['stream_file'] = session.get('stream_file')
        generate_uid_ck(configfile, session)
        play_tv(parameters, tmppath)

    elif 'mode' in parameters:
        generate_uid_ck(configfile, session)
        channel_list = channelhandler.get_channel_list(session)
        build_channel_menu(channel_list, lang=parameters.get('mode', 'all'))

    elif 'settings' in parameters:
        addon.openSettings()
    else:
        build_root_menu()


if __name__ == '__main__':
    main()
