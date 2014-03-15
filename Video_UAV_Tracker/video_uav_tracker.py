# -*- coding: utf-8 -*-
'''
**************************************************************************************************************************************
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

# Import the PyQt and QGIS libraries
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from ui_video_uav_tracker import Ui_Video_UAV_Tracker
import datetime
import osr           #from osgeo
from CanvasMarkers import PositionMarker
from ReplayMapTool import *
from pars import *
import os

from PyQt4.phonon import Phonon

#TABLE MANAGER IMPORT
from tableManagerUi import Ui_Dialog
from tableManagerUiRename import Ui_Rename
from tableManagerUiClone import Ui_Clone
from tableManagerUiInsert import Ui_Insert
import sys

class_pars = ParsFile()

class Video_UAV_Tracker:

    def __init__(self, iface):
        
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/Video_UAV_Tracker"
        # initialize locale
        localePath = ""
        locale = str(QSettings().value("locale/userLocale"))[0:2]

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/video_uav_tracker_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)


        # Create the dialog (after translation) and keep reference
        self.dlg = Video_UAV_TrackerDialog(iface)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
        QIcon(":/plugins/video_uav_tracker/icon.png"), u"Video UAV Tracker", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Video UAV Tracker", self.action)

        
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Video UAV Tracker", self.action)
        self.iface.removeToolBarIcon(self.action)

# run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()

            

class Video_UAV_TrackerDialog(QtGui.QDialog):
    def __init__(self,iface):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_Video_UAV_Tracker()
        self.ui.setupUi(self)
        self.iface = iface
        

        self.ui.sourceLoad_pushButton.clicked.connect(self.OpenButton)
        self.ui.replayPlay_pushButton.clicked.connect(self.PlayPauseButton)
        
        QObject.connect(self.ui.replay_mapTool_pushButton, SIGNAL("toggled(bool)"), self.replayMapTool_toggled)
        
        self.positionMarker=None
        
        settings = QSettings()
        settings.beginGroup("/plugins/PlayerPlugin")
        self.replay_followPosition = settings.value("followPosition", True, type=bool)
        settings.setValue("followPosition", self.replay_followPosition)
        
        QObject.connect(self.iface.mapCanvas(), SIGNAL("mapToolSet(QgsMapTool*)"), self.mapToolChanged)
        self.mapTool=ReplayMapTool(self.iface.mapCanvas(), self)
        self.mapTool_previous=None
        
        self.mapToolChecked = property(self.__getMapToolChecked, self.__setMapToolChecked)
        
        QObject.connect(self.ui.replayPosition_horizontalSlider, SIGNAL( 'sliderMoved(int)'), self.replayPosition_sliderMoved)
        #QObject.connect(self.ui.replayPosition_horizontalSlider, SIGNAL("actionTriggered(int)"), lambda x:self.replayPosition_sliderMoved())

        self.Partito = 0
        self.Chiudere = 0
        self.adactProjection = False
        self.INGV = 0
        self.videoWidget = Phonon.VideoWidget(self.ui.video_widget)

    
    def OpenButton(self):
        
        if self.Chiudere == 1:
            if self.positionMarker != None:
                self.iface.mapCanvas().scene().removeItem(self.positionMarker)
                self.positionMarker = None
            self.Chiudere = 0
            self.ui.replay_mapTool_pushButton.setChecked(False)
            self.ui.sourceLoad_pushButton.setText('Open...')
            self.INGV = 0
            self.timer.stop()
            self.timer2.stop()
            self.media_obj.stop()
            self.media_obj.clear()
            self.iface.mapCanvas().unsetMapTool(self.mapTool)
            self.close()
            
        else:
            
            
            if self.positionMarker != None:
                self.iface.mapCanvas().scene().removeItem(self.positionMarker)
                self.positionMarker = None
                
            try:
                self.path = QtGui.QFileDialog.getOpenFileName() 
                if not self.path is None:
                    gpxPath = self.path + '.gpx'
                    self.pathParts=gpxPath.split("/")

                    gpxFile=class_pars.parsfile(str(gpxPath))
            
         
                    self.gpxFile=gpxFile

                    self.GpxLayer=QgsVectorLayer((self.path + '.gpx')+"?type=track", self.pathParts[len(self.pathParts)-1]+" track", "gpx")

                
                
                    rendererv2 = self.GpxLayer.rendererV2()
                    rendererv2.symbol().setWidth( 3*rendererv2.symbol().width() )
                    #QgsMapLayerRegistry.instance().addMapLayer( self.GpxLayer )
                
                      
                    # create layer
                    #self.vl = QgsVectorLayer("Point?crs=epsg:4326&index=yes", self.pathParts[len(self.pathParts)-1]+" point", "memory")
                    #self.pr = self.vl.dataProvider()                            #moved some lines down
                    
                    #self.defaultDatabase == False
                    
                    SelectLayer,ok = QInputDialog.getItem(
                             self.iface.mainWindow(), 
                             "Layer chooser",
                             "Choose point layer",
                             ('Create new vector layer','Load existent vector layer','Load existent vector layer with default database') )
                    
                    if SelectLayer == 'Load existent vector layer':
                        self.newLayerPath = QtGui.QFileDialog.getOpenFileName()
                        if not self.newLayerPath is None:
                            name = self.newLayerPath.split("/")[-1][0:-4]
                            self.vl = QgsVectorLayer(self.newLayerPath, name, "ogr")
                            self.pr = self.vl.dataProvider()
                            QgsMapLayerRegistry.instance().addMapLayer( self.GpxLayer )                     
                            QgsMapLayerRegistry.instance().addMapLayer( self.vl )
                            
                    elif SelectLayer == 'Load existent vector layer with default database':
                        self.newLayerPath = QtGui.QFileDialog.getOpenFileName()
                        if not self.newLayerPath is None:
                            name = self.newLayerPath.split("/")[-1][0:-4]
                            self.vl = QgsVectorLayer(self.newLayerPath, name, "ogr")
                            self.pr = self.vl.dataProvider()
                            QgsMapLayerRegistry.instance().addMapLayer( self.GpxLayer )                     
                            QgsMapLayerRegistry.instance().addMapLayer( self.vl )
                            self.INGV = 1
                            
                    else:       
                        
                                
                        SelectDatabase,ok = QInputDialog.getItem(
                                 self.iface.mainWindow(), 
                                 "Select Database style",
                                 "Choose database",
                                 ('Post-earthquake assessment','Make your own...') )
                        
                        if SelectDatabase == 'Post-earthquake assessment':
                            
                            self.vl = QgsVectorLayer("Point?crs=epsg:4326&index=yes", self.pathParts[len(self.pathParts)-1]+" point", "memory")
                            self.pr = self.vl.dataProvider()
                            
                            
                        # add fields
                            self.pr.addAttributes( [ QgsField("id", QVariant.Int),
                                  QgsField('Building type', QVariant.String),
                                  QgsField('Vulnerability class', QVariant.String),                         
                                  QgsField('Structural type', QVariant.String),
                                  QgsField('Location', QVariant.String),
                                  QgsField('Damage level', QVariant.String),
                                  QgsField('Note', QVariant.String),
                                  QgsField('Land register number', QVariant.String),
                                  QgsField("Lon(WGS84)",  QVariant.String),
                                  QgsField("Lat(WGS84)", QVariant.String),
                                  QgsField('East UTM', QVariant.String),
                                  QgsField('Nord UTM',QVariant.String),
                                  QgsField('Image link', QVariant.String)
                                   ] )
                                  
                        # add a feature
                            fet = QgsFeature()
                            fet.setGeometry( QgsGeometry.fromPoint(QgsPoint(10,10)) )
                      
                            self.pr.addFeatures( [ fet ] )
                
                            # update layer's extent when new features have been added
                            # because change of extent in provider is not propagated to the layer
                            self.vl.updateExtents()
                        
                      
                            QgsMapLayerRegistry.instance().addMapLayer( self.GpxLayer )                     
                            QgsMapLayerRegistry.instance().addMapLayer( self.vl )
                            #QgsProject.instance().dirty( True )
                            self.INGV = 1
                            
                        else:
                            self.vl = QgsVectorLayer("Point?crs=epsg:4326&index=yes", self.pathParts[len(self.pathParts)-1]+" point", "memory")
                            self.pr = self.vl.dataProvider()
                            
                            self.dialoga = TableManager(self.iface, self.vl, self.pathParts,self.GpxLayer)
                            self.dialoga.exec_()    
                
                    
                 
                 



                palyr = QgsPalLayerSettings()           #set point label
                palyr.readFromLayer(self.vl)
                
                palyr.enabled = True
                palyr.fieldName = 'id'
                palyr.placement= QgsPalLayerSettings.Upright
                palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'14','')
                
                palyr.writeToLayer(self.vl) 
                
                
                                              
                if self.positionMarker==None:
                    self.positionMarker=PositionMarker(self.iface.mapCanvas())
        
            
                self.ui.replayPosition_label.setText('00:00:00' + '/' + str(datetime.timedelta(seconds = (int(class_pars.lst_dictionary[-1].get('second')))-(int(class_pars.lst_dictionary[0].get('second'))))))
                
                
                self.ui.replayPosition_horizontalSlider.setMinimum(0)
                self.ui.replayPosition_horizontalSlider.setMaximum(int(class_pars.lst_dictionary[-1].get('second'))-int(class_pars.lst_dictionary[0].get('second')))
            
                self.ui.replayPosition_horizontalSlider.setValue(0)

                
                self.media_src = Phonon.MediaSource(self.path)
                self.media_obj = Phonon.MediaObject(self)
                self.media_obj.setCurrentSource(self.media_src)
                Phonon.createPath(self.media_obj, self.videoWidget)
                audio_out = Phonon.AudioOutput(Phonon.VideoCategory, self)			#Phonon media_obj
                Phonon.createPath(self.media_obj, audio_out)
                self.ui.video_widget.resizeEvent = self.Resize()
                self.media_obj.setTickInterval(100)
                
                self.timer = QtCore.QTimer()
                self.timer2 = QtCore.QTimer()
                #QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.updateReplayPosition)
                #QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.SetSlide)
                QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.Timer)              #timer for refresh position and resize window
                QtCore.QObject.connect(self.timer2, QtCore.SIGNAL("timeout()"), self.Resize)
                
                self.media_obj.play()                       #phonon play

                #time.sleep(1)
                self.timer.start(1000)
                self.timer2.start(50)
                
                self.ui.replayPosition_label.setText('00:00:00' + '/' + str(datetime.timedelta(seconds = (int(class_pars.lst_dictionary[-1].get('second')))-(int(class_pars.lst_dictionary[0].get('second'))))))
                
                self.Partito = 1
            
                self.ui.sourceLoad_pushButton.setText('Close')
                self.Chiudere = 1             #load file selector
                
                
                
            except IOError :
                self.ui.sourceLoad_pushButton.setChecked(False)
                self.close()


                
                          
    def Resize(self):
          
        a = self.ui.video_widget.frameSize()
        b = self.videoWidget.frameSize()
        if a != b:
            self.videoWidget.resize(a)
        
        
        
            
    def CurrentPos(self):

        end = self.media_obj.totalTime()
        pos = self.media_obj.currentTime()
        remaining = self.media_obj.remainingTime()
        if pos == end:
            self.timer.stop()
            self.media_obj.pause()
            if self.Partito == 1:
                self.Partito = 0
            
            
        else:
            
            tmp2CurrentPos = (end - remaining)/1000
            
            temporary = (str(tmp2CurrentPos)).split('.')
            if int(temporary[-1]) <= 500:
                self.ui.replayPosition_label.setText(str(datetime.timedelta(seconds=int(tmp2CurrentPos))) + '/' + str(datetime.timedelta(seconds = (int(class_pars.lst_dictionary[-1].get('second')))-(int(class_pars.lst_dictionary[0].get('second'))))))
                return int(tmp2CurrentPos)
            else:
                self.ui.replayPosition_label.setText(str(datetime.timedelta(seconds=int(tmp2CurrentPos)+1)) + '/' + str(datetime.timedelta(seconds = (int(class_pars.lst_dictionary[-1].get('second')))-(int(class_pars.lst_dictionary[0].get('second'))))))
                return int(tmp2CurrentPos)+1
            
    def Timer(self):
        if self.Partito == 1:
            self.updateReplayPosition()
            self.SetSlide()
            #self.Resize()
        else:
            pass              

    def updateReplayPosition(self):
        '''update the position marker and the labels connecting the current video second to the corrisponding gps point'''
        if self.Partito == 1:                
            pos = self.CurrentPos()
            for i in range(len(class_pars.lst_dictionary)):
                current_seconds = int(int(class_pars.lst_dictionary[i].get('second')) - int(class_pars.lst_dictionary[0].get('second')))
                if current_seconds == pos:
                    self.lat,self.lon = float(class_pars.lst_dictionary[i].get('lat')) , float(class_pars.lst_dictionary[i].get('lon'))
                    self.Point = QgsPoint()
                    self.Point.set(self.lon,self.lat)
                    self.replay_currentAngle=class_pars.lst_dictionary[i].get('course')
            
                    self.ui.time.setText( 'Gps Time : ' + str(class_pars.lst_dictionary[i].get('time')))
                    self.ui.lat.setText ('Latitude : ' + str(class_pars.lst_dictionary[i].get('lat')))      
                    self.ui.lon.setText('Longitude : ' + str(class_pars.lst_dictionary[i].get('lon')))
                    self.ui.ele.setText('Elevation : ' + str(class_pars.lst_dictionary[i].get('ele'))+ '  mt.')
                    self.ui.speed.setText('Speed : ' + str(class_pars.lst_dictionary[i].get('speed')) + ' km/h')
                    
                    
            
                    #self.ui.replayPosition_horizontalSlider.setValue(pos)
                    
                    canvas = self.iface.mapCanvas()
                    mapRenderer = canvas.mapRenderer()
                    crsSrc = QgsCoordinateReferenceSystem(4326)    # .gpx is in WGS 84
                    crsDest = mapRenderer.destinationCrs()
                    
                    #crsDest = QgsCoordinateReferenceSystem(3857)  # WGS 84 Pseudo Mercator
                    xform = QgsCoordinateTransform(crsSrc, crsDest) #usage: xform.transform(QgsPoint)
            
                    
                    #if self.adactProjection == True:
                    self.positionMarker.setHasPosition(True)
                    self.Point = xform.transform(self.Point)
                    self.positionMarker.newCoords(self.Point)
                    self.positionMarker.angle=self.replay_currentAngle
            
                    if self.replay_followPosition:
                        extent=self.iface.mapCanvas().extent()
                    
                    boundaryExtent=QgsRectangle(extent)
                    boundaryExtent.scale(0.7)
                    if not boundaryExtent.contains(QgsRectangle(self.Point, self.Point)):
                        extentCenter= self.Point
                        newExtent=QgsRectangle(
                                    extentCenter.x()-extent.width()/2,
                                    extentCenter.y()-extent.height()/2,
                                    extentCenter.x()+extent.width()/2,
                                    extentCenter.y()+extent.height()/2
                                    )
                    
                        self.iface.mapCanvas().setExtent(newExtent)
                        self.iface.mapCanvas().refresh()
                    
    def PlayPauseButton(self):
        if self.Partito == 1:
            self.media_obj.pause()
            self.timer.stop()
            self.Partito = 0
        else:
            self.media_obj.play()
            self.timer.start(1000)
            self.Partito = 1
          
         
    def replayMapTool_toggled(self, checked):
        """Enable/disable replay map tool"""
        self.useMapTool(checked)        
            
    def useMapTool(self, use):
        """ afer you click on it, you can seek the video just clicking on the gps track """
        
        if use:
            if self.iface.mapCanvas().mapTool()!=self.mapTool:
                self.mapTool_previous=self.iface.mapCanvas().mapTool()
                self.iface.mapCanvas().setMapTool(self.mapTool)
        else:
            if self.mapTool_previous!=None:
                self.iface.mapCanvas().setMapTool(self.mapTool_previous)
            else:
                self.iface.mapCanvas().unsetMapTool(self.mapTool)        
        
    def mapToolChanged(self, tool):
        """Handle map tool changes outside  plugin"""
        if (tool!=self.mapTool) and self.mapToolChecked:
            self.mapTool_previous=None
            self.mapToolChecked=False
    
    def __getMapToolChecked(self):
        return self.replay_mapTool_pushButton.isChecked()
    def __setMapToolChecked(self, val):
        self.replay_mapTool_pushButton.setChecked(val)
        
    def findNearestPointInRecording(self, toPoint):
        """ Find the point nearest to the specified point (in map coordinates). """  
        
        
        for i in range(len(class_pars.lst_dictionary)):
            if (str(class_pars.lst_dictionary[i].get('lon')))[0:7] == (str(toPoint.x()))[0:7] and (str(class_pars.lst_dictionary[i].get('lat')))[0:7] == (str(toPoint.y()))[0:7]:
                #self.timer.stop()
                adj = int(class_pars.lst_dictionary[i].get('second')) - int(class_pars.lst_dictionary[0].get('second'))
                lat,lon = float(class_pars.lst_dictionary[i].get('lat')) , float(class_pars.lst_dictionary[i].get('lon'))
                Point = QgsPoint()
                Point.set(lon,lat)
                self.positionMarker.newCoords(Point)
                self.positionMarker.angle=class_pars.lst_dictionary[i].get('course')
                self.Seek(adj)
                break
                
                
        ''' to solve...
        
        dist = 1e20
        for i in range(len(class_pars.lst_dictionary)):
            d = abs(complex(float(class_pars.lst_dictionary[i].get('lon'))-toPoint.x(), float(class_pars.lst_dictionary[i].get('lat'))-toPoint.y()))
            if d<dist:
                self.timer.stop()
                adj = int(class_pars.lst_dictionary[i].get('second')) - int(class_pars.lst_dictionary[0].get('second'))
                lat,lon = float(class_pars.lst_dictionary[i].get('lat')) , float(class_pars.lst_dictionary[i].get('lon'))
                Point = QgsPoint()
                Point.set(lon,lat)
                self.positionMarker.newCoords(Point)
                self.positionMarker.angle=class_pars.lst_dictionary[i].get('course')
                self.Seek(adj)
                break
            
        '''
            
    def Seek (self, pos):
        if self.Partito == 0:
            self.timer.stop()
            self.media_obj.seek(pos*1000)
            self.media_obj.play()
            self.timer.start(1000)
            self.Partito = 1
            
        else:
            
            self.media_obj.seek(pos*1000)
            self.timer.start(1000)
    
    def replayPosition_sliderMoved(self,pos):
        """Handle moving of replay position slider by user """
        
        self.Seek(pos)
        
    def SetSlide(self):
        
        end = self.media_obj.totalTime()
        pos = self.media_obj.currentTime()
        if not pos == end:           
            pos = float(self.CurrentPos()) 
            self.ui.replayPosition_horizontalSlider.setValue(pos)
    '''    
    def adactProj(self, data):
        """Handle changing "checked" state of adact projection checkbox"""
        if data == 0:
            self.adactProjection = False
        else:
            self.adactProjection = True    
    '''
                
                
                
    def AddPoint(self,toPoint):
        
        
        if self.Partito == 1:
            self.media_obj.pause()
            self.timer.stop()
            self.Partito = 0
        else:
            pass
       
        a = self.vl.name()
        
        last_desc = '///'
        LayerName =str(a)
        last_desc2 = LayerName + ' Point N '
        fc = int(self.pr.featureCount())
        
        if self.INGV == 1:
                
            self.vl.dataProvider()
            
            filename = self.path + '__'+ 'tmp' + '.JPG'
            
            if os.name == 'posix':
                p = QPixmap.grabWindow(self.ui.video_widget.winId())
                
            else :
                p= QPixmap.grabWidget(self.videoWidget)                              #it change from linux version for Windows
                				                                                    
           
            p.save(filename)
            
            
    
            (Building_type,ok) = QInputDialog.getText(
                        self.iface.mainWindow(), 
                        "Attributes",
                        "Building type",
                        QLineEdit.Normal,
                        last_desc)
    
        
        
            (Vulnerability_class,ok) = QInputDialog.getItem(
                         self.iface.mainWindow(), 
                         "Attributes",
                         "Vulnerability class",
                         ['A','B','C','D','/'] , editable = False)
            
    
            
            (Structural_type,ok) = QInputDialog.getText(
                        self.iface.mainWindow(), 
                        "Attributes",
                        "Structural type",
                        QLineEdit.Normal,
                        last_desc)
            
            (Location,ok) = QInputDialog.getText(
                        self.iface.mainWindow(), 
                        "Attributes",
                        "Location",
                        QLineEdit.Normal,
                        last_desc2+str(fc))

                
            
            (Damage_level,ok) = QInputDialog.getItem(
                         self.iface.mainWindow(), 
                         "Attributes",
                         "Damage level",
                         ['1','2','3','4','5','/'], editable = False )
    
            (Note,ok) = QInputDialog.getText(
                        self.iface.mainWindow(), 
                        "Attributes",
                        "Note",
                        QLineEdit.Normal,
                        last_desc)
               
            (Land_register,ok) = QInputDialog.getText(
                        self.iface.mainWindow(), 
                        "Attributes",
                        "Land register number",
                        QLineEdit.Normal,
                        last_desc)
            
            
               
                #QMessageBox.information( self.iface.mainWindow(),"Feature Count", str(fc)) #"X,Y = %s,%s" % (str(point.x()),str(point.y())) )
                # create the feature
            feature = QgsFeature()
            lat,lon = toPoint.x(), toPoint.y()
            Point = QgsPoint()
            Point.set(lat,lon)
            EastUTM,NordUTM,alt= self.transform_wgs84_to_utm(lat, lon)
            
            feature.setGeometry(QgsGeometry.fromPoint(Point))
            
            if QGis.QGIS_VERSION_INT > 10800:
                    feature.setAttributes([fc, Building_type,Vulnerability_class,Structural_type,Location,Damage_level,Note,Land_register,lat,lon,EastUTM,NordUTM,self.path + '__'+ str(Location) + '.jpg'])
                    self.vl.startEditing()
                    self.vl.addFeature(feature, True)
                    self.vl.commitChanges()

                
            self.vl.setCacheImage(None)
            self.vl.triggerRepaint()
            
            
            os.rename(filename,self.path + '__'+ str(Location) + '.jpg')
            
        else:
            
            filename = self.path + '__'+ 'tmp' + '.JPG'
            
            if os.name == 'posix':
                p = QPixmap.grabWindow(self.ui.video_widget.winId())
                
            else :
                p= QPixmap.grabWidget(self.videoWidget)                              #it change from linux version for Windows
                                                                                    
            p.save(filename)
            
            
            fields = self.pr.fields()
            attributes = []
            lat,lon = toPoint.x(), toPoint.y()
            
            for field in fields:
                    a = str(field.name())
                    b = str(field.typeName())
                    if a == 'id':
                        fcnr = fc
                        attributes.append(fcnr)
                        
                    elif a == 'Lon(WGS84)':
                        attributes.append(lat)
                        
                    elif a == 'Location':
                        (Location,ok) = QInputDialog.getText(
                        self.iface.mainWindow(), 
                        "Attributes",
                        "Location",
                        QLineEdit.Normal,
                        last_desc2+str(fc))
                        attributes.append(Location)
                           
                    elif a == 'Lat(WGS84)':
                        attributes.append(lon)
                    elif a == 'East UTM':
                        EastUTM,NordUTM,alt = self.transform_wgs84_to_utm(lat, lon)
                        attributes.append(EastUTM)
                        
                    elif a == 'Nord UTM':
                        EastUTM,NordUTM,alt = self.transform_wgs84_to_utm(lat, lon)
                        attributes.append(NordUTM)
                        
                    elif a == 'Image link':
                        pass    
                    
                    else:
                        
                        if b == 'String':
           
                            (a,ok) = QInputDialog.getText(
                                                          self.iface.mainWindow(), 
                                                          "Attributes",
                                                          a + ' = String',
                                                          QLineEdit.Normal)
                            attributes.append(a)
                            
                    
                        elif b == 'Real':
                            
                            (a,ok) = QInputDialog.getDouble(
                                                            self.iface.mainWindow(), 
                                                            "Attributes",
                                                            a + ' = Real', decimals = 10)
                            attributes.append(a)

                        elif b == 'Integer':
                            
                            (a,ok) = QInputDialog.getInt(
                                                         self.iface.mainWindow(), 
                                                         "Attributes",
                                                         a + ' = Integer')
                            attributes.append(a)
                    
                    
                    
            
            feature = QgsFeature()
        
            Point = QgsPoint()
            Point.set(lat,lon)
            
            attributes.append(self.path + '__'+ str(Location) + '.jpg')
            
            feature.setGeometry(QgsGeometry.fromPoint(Point))
            
    
            feature.setAttributes(attributes)
            self.vl.startEditing()
            self.vl.addFeature(feature, True)
            self.vl.commitChanges()
            
                
            self.vl.setCacheImage(None)
            self.vl.triggerRepaint()
            
            
            os.rename(filename,self.path + '__'+ str(Location) + '.jpg')         
                    
    def transform_wgs84_to_utm(self, lon, lat):    
        def get_utm_zone(longitude):
            return (int(1+(longitude+180.0)/6.0))

        def is_northern(latitude):
            """
            Determines if given latitude is a northern for UTM
            """
            if (latitude < 0.0):
                return 0
            else:
                return 1

        utm_coordinate_system = osr.SpatialReference()
        utm_coordinate_system.SetWellKnownGeogCS("WGS84") # Set geographic coordinate system to handle lat/lon  
        utm_coordinate_system.SetUTM(get_utm_zone(lon), is_northern(lat))

        wgs84_coordinate_system = utm_coordinate_system.CloneGeogCS() # Clone ONLY the geographic coordinate system 

        # create transform component
        wgs84_to_utm_transform = osr.CoordinateTransformation(wgs84_coordinate_system, utm_coordinate_system) # (<from>, <to>)
        return wgs84_to_utm_transform.TransformPoint(lon, lat, 0) # returns easting, northing, altitude 
        
        
        
        
        
        
########## CLASS DialogRename ##############################

class DialogRename(QDialog, Ui_Rename):
    
        def __init__(self, iface, fields, selection):
            QDialog.__init__(self)
            self.iface = iface
            self.setupUi(self)
            self.fields = fields
            self.selection = selection
            self.setWindowTitle(self.tr('Rename field: {0}').format(fields[selection].name()))
            self.lineEdit.setValidator(QRegExpValidator(QRegExp('[\w\ _]{,10}'),self))
            self.lineEdit.setText(fields[selection].name())
    
    
        def accept(self):
            
            if self.newName() == self.fields[self.selection].name():
                QDialog.reject(self)
                return
        
            for i in self.fields.values():
                if self.newName().upper() == i.name().upper() and i != self.fields[self.selection]:
                    QMessageBox.warning(self,self.tr('Rename field'),self.tr('There is another field with the same name.\nPlease type different one.'))
                    return
                
                if not self.newName():
                    QMessageBox.warning(self,self.tr('Rename field'),self.tr('The new name cannot be empty'))
                    self.lineEdit.setText(self.fields[self.selection].name())
                    return
                QDialog.accept(self)
    
        def newName(self):
            return self.lineEdit.text()



########## CLASS DialogClone ##############################

class DialogClone(QDialog, Ui_Clone):
  def __init__(self, iface, fields, selection):
    QDialog.__init__(self)
    self.iface = iface
    self.setupUi(self)
    self.fields = fields
    self.selection = selection
    self.setWindowTitle(self.tr('Clone field: ')+fields[selection].name())
    self.comboDsn.addItem(self.tr('at the first position'))
    for i in range(len(fields)):
      self.comboDsn.addItem(self.tr('after the {0} field').format(fields[i].name()))
    self.comboDsn.setCurrentIndex(selection+1)
    self.lineDsn.setValidator(QRegExpValidator(QRegExp('[\w\ _]{,10}'),self))
    self.lineDsn.setText(fields[selection].name()[:8] + '_2')

  def accept(self):
    if not self.result()[1]:
      QMessageBox.warning(self,self.tr('Clone field'),self.tr('The new name cannot be empty'))
      return
    if self.result()[1] == self.fields[self.selection].name():
        QMessageBox.warning(self,self.tr('Clone field'),self.tr('The new field\'s name must be different then source\'s one!'))
        return
    for i in self.fields.values():
      if self.result()[1].upper() == i.name().upper():
        QMessageBox.warning(self,self.tr('Clone field'),self.tr('There is another field with the same name.\nPlease type different one.'))
        return
    QDialog.accept(self)

  def result(self):
    return self.comboDsn.currentIndex(), self.lineDsn.text()



########## CLASS DialogInsert ##############################

class DialogInsert(QDialog, Ui_Insert):
  def __init__(self, iface, fields, selection):
    QDialog.__init__(self)
    self.iface = iface
    self.setupUi(self)
    self.fields = fields
    self.selection = selection
    self.setWindowTitle(self.tr('Insert field'))
    self.lineName.setValidator(QRegExpValidator(QRegExp('[\w\ _]{,10}'),self))
    self.comboType.addItem(self.tr('Integer'))
    self.comboType.addItem(self.tr('Real'))
    self.comboType.addItem(self.tr('String'))
    self.comboPos.addItem(self.tr('at the first position'))
    for i in range(len(fields)):
      self.comboPos.addItem(self.tr('after the {0} field').format(fields[i].name()))
    self.comboPos.setCurrentIndex(selection+1)

  def accept(self):
    if not self.result()[0]:
      QMessageBox.warning(self,self.tr('Insert new field'),self.tr('The new name cannot be empty'))
      return
    for i in self.fields.values():
      if self.result()[0].upper() == i.name().upper():
        QMessageBox.warning(self,self.tr('Insert new field'),self.tr('There is another field with the same name.\nPlease type different one.'))
        return
    QDialog.accept(self)

  def result(self):
    return self.lineName.text(), self.comboType.currentIndex(), self.comboPos.currentIndex()



########## CLASS TableManager ##############################

class TableManager(QDialog, Ui_Dialog):

  def __init__(self, iface, vl, pathParts,gpxLayer):
    QDialog.__init__(self)
    self.iface = iface
    self.setupUi(self)
    self.layer = vl
    self.GpxLayer = gpxLayer
    self.provider = self.layer.dataProvider()
    self.fields = self.readFields( self.provider.fields() )
    self.isUnsaved = False  # No unsaved changes yet
    if self.provider.storageType() == 'ESRI Shapefile': # Is provider saveable?
      self.isSaveable = True
    else:
      self.isSaveable = False
    self.pathParts = pathParts
    self.needsRedraw = True # Preview table is redrawed only on demand. This is for initial drawing.
    self.lastFilter = None
    self.selection = -1     # Don't highlight any field on startup
    self.selection_list = [] #Update: Santiago Banchero 09-06-2009

    QObject.connect(self.butUp, SIGNAL('clicked()'), self.doMoveUp)
    QObject.connect(self.butDown, SIGNAL('clicked()'), self.doMoveDown)
    QObject.connect(self.butDel, SIGNAL('clicked()'), self.doDelete)
    QObject.connect(self.butIns, SIGNAL('clicked()'), self.doInsert)
    QObject.connect(self.butClone, SIGNAL('clicked()'), self.doClone)
    QObject.connect(self.butRename, SIGNAL('clicked()'), self.doRename)
    QObject.connect(self.butSaveAs, SIGNAL('clicked()'), self.doSaveAs)
    #QObject.connect(self.butSaveStyle, SIGNAL('clicked()'), self.SaveStyle)
    QObject.connect(self.fieldsTable, SIGNAL('itemSelectionChanged ()'), self.selectionChanged)
    QObject.connect(self.tabWidget, SIGNAL('currentChanged (int)'), self.drawDataTable)
    #QObject.connect(self.butStandardFields, SIGNAL('clicked()'), self.INGVdatabaseBUT)
    
    self.setWindowTitle(self.tr('Table Manager: {0}').format(self.layer.name()))
    
    self.drawFieldsTable()
    self.readData()


  def readFields(self, providerFields): # Populates the self.fields dictionary with providerFields
    fieldsDict = {}
    i=0
    for field in providerFields:
        fieldsDict.update({i:field})
        i+=1
    return fieldsDict



  def drawFieldsTable(self): # Draws the fields table on startup and redraws it when changed
    fields = self.fields
    self.fieldsTable.setRowCount(0)
    for i in range(len(fields)):
      self.fieldsTable.setRowCount(i+1)
      item = QTableWidgetItem(fields[i].name())
      item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
      item.setData(Qt.UserRole, i) # set field index
      self.fieldsTable.setItem(i,0,item)
      item = QTableWidgetItem(fields[i].typeName())
      item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
      self.fieldsTable.setItem(i,1,item)
    self.fieldsTable.setColumnWidth(0, 128)
    self.fieldsTable.setColumnWidth(1, 64)



  def readData(self): # Reads data from the 'provider' QgsDataProvider into the 'data' list [[column1] [column2] [column3]...]
    fields = self.fields
    self.data = []
    for i in range(len(fields)):
      self.data += [[]]
    steps = self.provider.featureCount()
    stepp = steps / 10
    if stepp == 0:
      stepp = 1
    progress = self.tr('Reading data ') # As a progress bar is used the main window's status bar, because the own one is not initialized yet
    n = 0
    for feat in self.provider.getFeatures():
        attrs = feat.attributes()

        for i in range(len(attrs)):
            self.data[i] += [attrs[i]]

        n += 1
        if n % stepp == 0:
            progress += '|'
            self.iface.mainWindow().statusBar().showMessage(progress)

    self.iface.mainWindow().statusBar().showMessage('')



  def drawDataTable(self,tab): # Called when user switches tabWidget to the Table Preview
    if tab != 1 or self.needsRedraw == False: return
    fields = self.fields
    self.dataTable.clear()
    self.repaint()
    self.dataTable.setColumnCount(len(fields))
    self.dataTable.setRowCount(self.provider.featureCount())
    header = []
    for i in fields.values():
      header.append(i.name())
    self.dataTable.setHorizontalHeaderLabels(header)
    formatting = True
    if formatting: # slower procedure, with formatting the table items
      for i in range(len(self.data)):
        for j in range(len(self.data[i])):
          item = QTableWidgetItem(unicode(self.data[i][j] or 'NULL'))
          item.setFlags(Qt.ItemIsSelectable)
          if fields[i].type() == 6 or fields[i].type() == 2:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
          self.dataTable.setItem(j,i,item)
    else: # about 25% faster procedure, without formatting
      for i in range(len(self.data)):
        for j in range(len(self.data[i])):
          self.dataTable.setItem(j,i,QTableWidgetItem(unicode(self.data[i][j] or 'NULL')))
    self.dataTable.resizeColumnsToContents()
    self.needsRedraw = False



  def setChanged(self): # Called after making any changes
    if self.isSaveable:
      self.butSave.setEnabled(True)
    self.butSaveAs.setEnabled(True)
    self.isUnsaved = True       # data are unsaved
    self.needsRedraw = True     # preview table needs to redraw



  def selectionChanged(self): # Called when user is changing field selection of field
    #self.selection_list = [ i.topRow() for i in self.fieldsTable.selectedRanges() ]
    self.selection_list = [i for i in range(self.fieldsTable.rowCount()) if self.fieldsTable.item(i,0).isSelected()]

    if len(self.selection_list)==1:
        self.selection = self.selection_list[0]
    else:
        self.selection = -1

    self.butDel.setEnabled( len(self.selection_list)>0 )

    item = self.selection
    if item == -1:
      self.butUp.setEnabled(False)
      self.butDown.setEnabled(False)
      self.butRename.setEnabled(False)
      self.butClone.setEnabled(False)
    else:
      if item == 0:
        self.butUp.setEnabled(False)
      else:
        self.butUp.setEnabled(True)
      if item == self.fieldsTable.rowCount()-1:
        self.butDown.setEnabled(False)
      else:
        self.butDown.setEnabled(True)
      if self.fields[item].type() in [2,6,10]:
         self.butRename.setEnabled(True)
         self.butClone.setEnabled(True)
      else:
        self.butRename.setEnabled(False)
        self.butClone.setEnabled(False)



  def doMoveUp(self): # Called when appropriate button was pressed
    item = self.selection
    tmp = self.fields[item]
    self.fields[item] = self.fields[item-1]
    self.fields[item-1] = tmp
    for i in range(0,2):
      tmp = QTableWidgetItem(self.fieldsTable.item(item,i))
      self.fieldsTable.setItem(item,i,QTableWidgetItem(self.fieldsTable.item(item-1,i)))
      self.fieldsTable.setItem(item-1,i,tmp)
    if item > 0:
      self.fieldsTable.clearSelection()
      self.fieldsTable.setCurrentCell(item-1,0)
    tmp = self.data[item]
    self.data[item]=self.data[item-1]
    self.data[item-1]=tmp
    self.setChanged()



  def doMoveDown(self): # Called when appropriate button was pressed
    item = self.selection
    tmp = self.fields[item]
    self.fields[self.selection] = self.fields[self.selection+1]
    self.fields[self.selection+1] = tmp
    for i in range(0,2):
      tmp = QTableWidgetItem(self.fieldsTable.item(item,i))
      self.fieldsTable.setItem(item,i,QTableWidgetItem(self.fieldsTable.item(item+1,i)))
      self.fieldsTable.setItem(item+1,i,tmp)
    if item < self.fieldsTable.rowCount()-1:
      self.fieldsTable.clearSelection()
      self.fieldsTable.setCurrentCell(item+1,0)
    tmp = self.data[item]
    self.data[item]=self.data[item+1]
    self.data[item+1]=tmp
    self.setChanged()



  def doRename(self): # Called when appropriate button was pressed
    dlg = DialogRename(self.iface,self.fields,self.selection)
    if dlg.exec_() == QDialog.Accepted:
      newName = dlg.newName()
      self.fields[self.selection].setName(newName)
      item = self.fieldsTable.item(self.selection,0)
      item.setText(newName)
      self.fieldsTable.setItem(self.selection,0,item)
      self.fieldsTable.setColumnWidth(0, 128)
      self.fieldsTable.setColumnWidth(1, 64)
      self.setChanged()



  def doDelete(self): # Called when appropriate button was pressed
    #<---- Update: Santiago Banchero 09-06-2009 ---->
    #self.selection_list = sorted(self.selection_list,reverse=True)
    all_fields_to_del = [self.fields[i].name() for i in self.selection_list if i <> -1]

    warning = self.tr('Are you sure you want to remove the following fields?\n{0}').format(", ".join(all_fields_to_del))
    if QMessageBox.warning(self, self.tr('Delete field'), warning , QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
        return

    self.selection_list.sort(reverse=True) # remove them in reverse order to avoid index changes!!!
    for r in self.selection_list:
        if r <> -1:
            del(self.data[r])
            del(self.fields[r])
            self.fields = dict(zip(range(len(self.fields)), self.fields.values()))
            self.drawFieldsTable()
            self.setChanged()

    self.selection_list = []
    #</---- Update: Santiago Banchero 09-06-2009 ---->


  def doInsert(self): # Called when appropriate button was pressed
    dlg = DialogInsert(self.iface,self.fields,self.selection)
    if dlg.exec_() == QDialog.Accepted:
      (aName, aType, aPos) = dlg.result()
      if aType == 0:
        aLength = 10
        aPrec = 0
        aVariant = QVariant.Int
        aTypeName = 'Integer'
      elif aType == 1:
        aLength = 32
        aPrec = 3
        aVariant = QVariant.Double
        aTypeName = 'Real'
      else:
        aLength = 80
        aPrec = 0
        aVariant = QVariant.String
        aTypeName = 'String'
      self.data += [[]]
      if aPos < len(self.fields):
        fieldsToMove = range(aPos+1,len(self.fields)+1)
        fieldsToMove.reverse()
        for i in fieldsToMove:
          self.fields[i] = self.fields[i-1]
          self.data[i] = self.data[i-1]
      self.fields[aPos] = QgsField(aName, aVariant, aTypeName, aLength, aPrec, "")
      aData = []
      if aType == 2:
        aItem = None
      else:
        aItem = None
      for i in range(len(self.data[0])):
        aData += [aItem]
      self.data[aPos] = aData
      self.drawFieldsTable()
      self.fieldsTable.setCurrentCell(aPos,0)
      self.setChanged()



  def doClone(self): # Called when appropriate button was pressed
    dlg = DialogClone(self.iface,self.fields,self.selection)
    if dlg.exec_() == QDialog.Accepted:
      (dst, newName) = dlg.result()
      self.data += [[]]
      movedField = QgsField(self.fields[self.selection])
      movedData = self.data[self.selection]
      if dst < len(self.fields):
        fieldsToMove = range(dst+1,len(self.fields)+1)
        fieldsToMove.reverse()
        for i in fieldsToMove:
          self.fields[i] = self.fields[i-1]
          self.data[i] = self.data[i-1]
      self.fields[dst] = movedField
      self.fields[dst].setName(newName)
      self.data[dst] = movedData
      self.drawFieldsTable()
      self.fieldsTable.setCurrentCell(dst,0)
      self.setChanged()


  def doSaveAs(self): # write data to memory layer
      
    #QgsMapLayerRegistry.instance().removeAllMapLayers()        
    
    # create destination layer
    fields = QgsFields()
    keys = self.fields.keys()
    keys.sort()
    for key in keys:
        fields.append(self.fields[key])
        
   

    qfields = []
    for field in fields:
        qfields.append(field)
        
    self.provider.addAttributes([QgsField('id', QVariant.Int)])
        
    self.provider.addAttributes(qfields)
        
    self.provider.addAttributes([QgsField('Location', QVariant.String),
          QgsField("Lon(WGS84)",  QVariant.String),
          QgsField("Lat(WGS84)", QVariant.String),
          QgsField('East UTM', QVariant.String),
          QgsField('Nord UTM',QVariant.String),
          QgsField('Image link', QVariant.String)])    
        
    fet = QgsFeature()
    fet.setGeometry( QgsGeometry.fromPoint(QgsPoint(10,10)) )
                
    self.provider.addFeatures( [ fet ] )  
   
    self.layer.updateExtents()
   
    QgsMapLayerRegistry.instance().addMapLayer( self.GpxLayer )
    QgsMapLayerRegistry.instance().addMapLayer( self.layer )
    
    QgsProject.instance().dirty( True )
    
    
    
    
    self.close()
                 
      
  def SaveStyle(self):
      pass
      
      self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/video_uav_tracker"
      
      (StyleName,ok) = QInputDialog.getText(
                        self.iface.mainWindow(), 
                        "Save profile",
                        "Type profile name",
                        QLineEdit.Normal,
                        '  ')
      
      profile_file = open(self.plugin_dir + StyleName + '.txt', 'w') 
      for field in self.fields:
          profile_file.write(str(self.readFields(self.fields)))
          
      profile_file.close()    
      
      
