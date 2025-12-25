'''
video_proj module
will send the video played on any of VLC or Media Player on the desired display
- on one display will be sent in maximize at start
- on different display will be restored at stop
'''
import screeninfo       # pylint: disable=import-error
import pygetwindow

class VideoProjection:
    '''Video Projection class'''
    def __init__(self, app_list):
        self.__monitor = None #get_monitor_info(display)
        self.applications = app_list

    def screen_optimizer(self, display, fullscreen=False):
        '''optimize to run window on specified monitor'''
        print("screen_optimizer: display=", display, "fullscreen =", fullscreen)
        self.__monitor = get_monitor_info(display)
        #print("screen_optimizer: self.__monitor=", self.__monitor)

        win_list = []
        for item in self.applications:
            #win_list = get_win_by_title(self.applications[0])
            win_list.extend(get_win_by_title(item))

        #print("win_list =", win_list)
        if win_list:
        #    reshape_window(fullscreen, self.__monitor, win_list[0])
            for item in win_list:
                reshape_window(fullscreen, self.__monitor, item)

            return True

        return False


def get_monitor_info(mon_name):
    '''get the monitor info'''
    mon_list = screeninfo.get_monitors()
    for item in mon_list:
        if mon_name in item.name:
            return item
    return None

def get_win_by_title(title):
    '''get the window by title name'''
    return pygetwindow.getWindowsWithTitle(title)

def calculate_win_size(matrix: int, monitor: dict):
    '''
    Dividing apps on monitors by calculating the size of each windows
        based on the monitor resolution
    Args:
        matrix (int): reprezents the number of lines and colomns in the square matrix
        monitor (dict): monitor information from config_parser
    Returns:
        win_size_info (dict) a dictionary containing the width, height of the windows
                             and the top left monitor
    '''
    win_size_info = {}
    width = monitor.width #monitor['width']
    height = monitor.height - 20 # monitor['height'] - 20

    win_size_info['width'] = width/matrix
    win_size_info['height'] = height/matrix
    win_size_info['end_screen'] = width + monitor.x

    return win_size_info

def reshape_window(fullscreen, monitor, win):
    '''reshape the window'''

    location_x = monitor.x
    location_y = monitor.y

    #win.restore()
    #print(location_x, location_y)
    if fullscreen:
        calculate_win_size(1, monitor)
        win.moveTo(int(location_x), int(location_y))
        win.maximize()
    else:
        win.restore()
        calculate_win_size(1, monitor)
        win.resizeTo(800, 500)
        win.moveTo(int(location_x), int(location_y))
