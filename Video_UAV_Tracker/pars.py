# -*- coding: utf-8 -*-

'''
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

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''




import time
import re
import random
#from BeautifulSoup import BeautifulStoneSoup
from parser import BeautifulStoneSoup

class ParsFile:

    def parsfile(self, filename):
        handler = open(filename).read()
        soup = BeautifulStoneSoup(handler)
        dictionary = {}
        self.lst_dictionary = []
        for trkpt in soup.findAll('trkpt'):
            arr_lat_lon = trkpt.attrs
            arr_ele = trkpt.ele
            arr_ele = arr_ele.renderContents()
            eletmp = re.split(r'[<>,;]+', (str(arr_ele)))
            arr_time = trkpt.time
            arr_time = arr_time.renderContents()
            arr_course = trkpt.course
            arr_speed = trkpt.speed
            try:
                arr_time = time.strptime(arr_time[:-6], '%Y-%m-%dT%H.%M.%S')
            except ValueError:
                try:
                    arr_time = time.strptime(arr_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                except:
                    arr_time = time.strptime(arr_time, '%Y-%m-%dT%H:%M:%SZ')
            t = arr_time
            try:
                dictionary,dictionary[u'ele'],dictionary[u'time'],dictionary[u'speed'],dictionary[u'course'] = dict(trkpt.attrs),eletmp[0][0:6],str(t.tm_mday)+' '+ str(t.tm_mon)+' '+ str(t.tm_year)+' '+ str(t.tm_hour)+':'+ str(t.tm_min)+':'+ str(t.tm_sec),str(arr_speed)[7:11] ,float(str(arr_course)[8:-9])
            except ValueError:
                dictionary,dictionary[u'ele'],dictionary[u'time'],dictionary[u'speed'],dictionary[u'course'] = dict(trkpt.attrs),eletmp[0][0:6],str(t.tm_mday)+' '+ str(t.tm_mon)+' '+ str(t.tm_year)+' '+ str(t.tm_hour)+':'+ str(t.tm_min)+':'+ str(t.tm_sec),str(arr_speed)[7:11], float(random.randrange(0,360))

                
            current_second = int(arr_time[3]) * 60 * 60 + int(arr_time[4]) * 60 + int(arr_time[5])
            dictionary[u'second'] = unicode(current_second)
            self.lst_dictionary.append(dictionary)
        #print self.lst_dictionary
	   
	
        many_seconds_start = int(self.lst_dictionary[0].get('second'))
        many_seconds_finish = int(self.lst_dictionary[-1].get('second'))
        self.many_seconds = many_seconds_finish - many_seconds_start
	
