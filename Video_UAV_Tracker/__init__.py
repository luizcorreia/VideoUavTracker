# -*- coding: utf-8 -*-
"""
/*************************************************************************************************************************************
 Video_UAV_Tracker                                                                                                                   *
                                 A QGIS plugin                                                                                       *     
 Replay a video in sync with a gps track displayed on the map                                                                        *
                              -------------------                                                                                    *
        begin                : 2013-09-02                                                                                            *
        copyright            : (C) 2013 by Salvatore Agosta / Università di Bologna / SAL Engineering                                *
        email                : sagost@katamail.com                                                                                   *
        website              : http://www.salengineering.it/                                                                         * 
                                                                                                                                     *   
I stole some part of the code from Table Manager Qgis Plugin, written by Borys Jurgiel, http://hub.qgis.org/projects/tablemanager.   * 
And from Qgismapper Player Plugin too, http://code.google.com/p/qgismapper/.                                                         *   
Thanks to both of you!                                                                                                               *
**************************************************************************************************************************************
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "Video UAV Tracker"


def description():
    return "Replay a video in sync with a gps track displayed on the map"


def version():
    return "1.2.3.1"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "2.0"
    
def experimental():
    return False    

def author():
    return "Salvatore Agosta / Università di Bologna / SAL Engineering"

def email():
    return "sagost@katamail.com"

def classFactory(iface):
    # load Video_UAV_Tracker class from file Video_UAV_Tracker
    from video_uav_tracker import Video_UAV_Tracker
    return Video_UAV_Tracker(iface)
