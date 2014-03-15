**************************************************************************************************************************************
 Video_UAV_Tracker    vers. 1.2                                                                                                  *
                                 A QGIS plugin                                                                                       *     
 Replay a video in sync with a gps track displayed on the map                                                                        *
                              -------------------                                                                                    *
        begin                : 2013-09-02                                                                                            *
        copyright            : (C) 2013 by Salvatore Agosta / Universita' di Bologna / SAL Engineering                               *
        email                : sagost@katamail.com                                                                                   *
        website              : http://www.salengineering.it/                                                                         * 
                                                                                                                                     *   
I took some part of the code from Table Manager Qgis Plugin, written by Borys Jurgiel, http://hub.qgis.org/projects/tablemanager.    * 
And from Qgismapper Player Plugin too, http://code.google.com/p/qgismapper/.                                                         *   
Thanks to both of you!  And to Andrea Ginesi.                                                                                        *
**************************************************************************************************************************************

****************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************
 
 -ATTENTION-        ##########     ONLY 64 bit systems are admitted ############
 
 
 
 
 -INTRODUCTION-
 
 Video UAV Tracker is a simple Qgis plugin to view your video in sync with a gps track displayed on a map. 
 It was developed under the Geomatics Laboratory (University of Bologna sect. of Geography) leaded by prof. Marco Dubbini, in collaboration
 with prof. Romano Camassi from the Bologna's section of INGV (National Institute Geophisics and Vulcanology).
Video UAV Tracker provide a rapid quality analysis tools for INGV and Civil Protection analyst in Post-Hazard condition (that's why the default
database is setted like this).




-HOW TO-

If you want to use Video UAV Tracker you need a video and a gpx file ( 1 point per second) in sync and with the same lenght.
To do that you can do like this:

-1 When you start the video, focus on a GPS time. (Attention, if you are focusing on a NMEA string the time string could be an UTC time, that 
diff from GPS time by 16 seconds now (it change year after year)

-2 Calculate the start time and the end time of the video on the GPS time.

-3 Cut the video to fit the .gpx file with a video editor

-4 Set the same name for video and gpx file and put theme in the same folder. (if the video name is "MOVIETEST.MP4" the gpx file will be "MOVIETEST.MP4.gpx" )

-5 When you start the Plugin, after pushing the Open button, you have to select the video file, not the gpx one.

Done.



-FEATURES


-Pushing "Map Tool" button you can seek the video left-clicking on or near the gpx track, and if you right-click anywhere a Point will be created and all
attributes will be asked to be filled. (Location attributes is the name of the screenshot file, so change it every time or the new screenshot will overwrite the old one) 

-For every point a screenshot will be taken and saved in the video folder. Screenshot dimension depend on the dimension of the player window.

-It loads automatically a memory layer with automatic attributes (progressive id , UTM coordinates , Latitude and Longitude, and the path to the screenshot)

-You can assign to the layer the default database (made for INGV analyst), or make your own with the TABLE MANAGER

-You can load an existent layer and continue with your work.

-It run smoothly also with Open Layers plugin



-TO LINUX USER-

The video player use Gstreamer as backends. Install it if you don't have it.


-TO MAC OSX USER-

If you want to use it you need to install Phonon module in your Qgis Python






-TO WINDOWS USER-

The video player use usually Windows Media Player as backends, if the video window remain black try to install the K-Lite FULL codecs pack. 

Double screen use is suggested, or without having two screens is recommended to resize the two windows.














 
 