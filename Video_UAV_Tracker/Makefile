#/***************************************************************************
# Video_UAV_Tracker
# 
# Replay a video in sync with a gps track displayed on the map
#                             -------------------
#        begin                : 2013-09-02
#        copyright            : (C) 2013 by Salvatore Agosta / Università di Bologna
#        email                : sagost@katamail.com
# ***************************************************************************/
# 
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

# CONFIGURATION
PLUGIN_UPLOAD = $(CURDIR)/plugin_upload.py

# Makefile for a PyQGIS plugin 

# translation
SOURCES = video_uav_tracker.py ui_video_uav_tracker.py __init__.py video_uav_trackerdialog.py
#TRANSLATIONS = i18n/video_uav_tracker_en.ts
TRANSLATIONS = 

# global

PLUGINNAME = video_uav_tracker

PY_FILES = video_uav_tracker.py  __init__.py

EXTRAS = icon.png 

UI_FILES = ui_video_uav_tracker.py

RESOURCE_FILES = resources_rc.py

HELP = help/build/html

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

%.py : %.ui
	pyuic4 -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# /usr/share/qgis/python/plugins/VUT Qgis Plugin
deploy: compile doc transcompile
	mkdir -p /usr/share/qgis/python/plugins$(PLUGINNAME)
	cp -vf $(PY_FILES) /usr/share/qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) /usr/share/qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) /usr/share/qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) /usr/share/qgis/python/plugins/$(PLUGINNAME)
	cp -vfr i18n /usr/share/qgis/python/plugins/$(PLUGINNAME)
	cp -vfr $(HELP) /usr/share/qgis/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find /usr/share/qgis/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find /usr/share/qgis/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf /usr/share/qgis/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean 
	rm -f $(PLUGINNAME).zip
	cd /usr/share/qgis/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

# Create a zip package of the plugin named $(PLUGINNAME).zip. 
# This requires use of git (your plugin development directory must be a 
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
package: compile
		rm -f $(PLUGINNAME).zip
		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
		echo "Created package: $(PLUGINNAME).zip"

upload: zip
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

# transup
# update .ts translation files
transup:
	pylupdate4 Makefile

# transcompile
# compile translation files into .qm binary format
transcompile: $(TRANSLATIONS:.ts=.qm)

# transclean
# deletes all .qm files
transclean:
	rm -f i18n/*.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

# build documentation with sphinx
doc: 
	cd help; make html
