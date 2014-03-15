# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_video_uav_tracker.ui'
#
# Created: Mon Oct 14 09:58:42 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Video_UAV_Tracker(object):
    def setupUi(self, Video_UAV_Tracker):
        Video_UAV_Tracker.setObjectName(_fromUtf8("Video_UAV_Tracker"))
        Video_UAV_Tracker.resize(512, 507)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Video_UAV_Tracker.sizePolicy().hasHeightForWidth())
        Video_UAV_Tracker.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(Video_UAV_Tracker)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.replayPosition_label = QtGui.QLabel(Video_UAV_Tracker)
        self.replayPosition_label.setObjectName(_fromUtf8("replayPosition_label"))
        self.gridLayout.addWidget(self.replayPosition_label, 2, 2, 1, 1)
        self.video_widget = QtGui.QWidget(Video_UAV_Tracker)
        #self.video_widget.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 0);"))
        self.video_widget.setObjectName(_fromUtf8("video_widget"))
        self.gridLayout.addWidget(self.video_widget, 0, 0, 1, 4)
        self.replay_mapTool_pushButton = QtGui.QPushButton(Video_UAV_Tracker)
        self.replay_mapTool_pushButton.setCheckable(True)
        self.replay_mapTool_pushButton.setObjectName(_fromUtf8("replay_mapTool_pushButton"))
        self.gridLayout.addWidget(self.replay_mapTool_pushButton, 2, 3, 1, 1)
        self.replayPlay_pushButton = QtGui.QPushButton(Video_UAV_Tracker)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.replayPlay_pushButton.sizePolicy().hasHeightForWidth())
        self.replayPlay_pushButton.setSizePolicy(sizePolicy)
        self.replayPlay_pushButton.setCheckable(False)
        self.replayPlay_pushButton.setChecked(False)
        self.replayPlay_pushButton.setObjectName(_fromUtf8("replayPlay_pushButton"))
        self.gridLayout.addWidget(self.replayPlay_pushButton, 2, 1, 1, 1)
        self.replayPosition_horizontalSlider = QtGui.QSlider(Video_UAV_Tracker)
        self.replayPosition_horizontalSlider.setTracking(False)
        self.replayPosition_horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.replayPosition_horizontalSlider.setObjectName(_fromUtf8("replayPosition_horizontalSlider"))
        self.gridLayout.addWidget(self.replayPosition_horizontalSlider, 1, 0, 1, 4)
        self.sourceLoad_pushButton = QtGui.QPushButton(Video_UAV_Tracker)
        self.sourceLoad_pushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.sourceLoad_pushButton.setObjectName(_fromUtf8("sourceLoad_pushButton"))
        self.gridLayout.addWidget(self.sourceLoad_pushButton, 2, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.groupBox = QtGui.QGroupBox(Video_UAV_Tracker)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QtCore.QSize(22222, 97))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.ele = QtGui.QLabel(self.groupBox)
        self.ele.setGeometry(QtCore.QRect(0, 60, 579, 16))
        self.ele.setObjectName(_fromUtf8("ele"))
        self.time = QtGui.QLabel(self.groupBox)
        self.time.setGeometry(QtCore.QRect(0, 0, 579, 17))
        self.time.setFocusPolicy(QtCore.Qt.NoFocus)
        self.time.setObjectName(_fromUtf8("time"))
        self.lat = QtGui.QLabel(self.groupBox)
        self.lat.setGeometry(QtCore.QRect(0, 20, 579, 16))
        self.lat.setObjectName(_fromUtf8("lat"))
        self.lon = QtGui.QLabel(self.groupBox)
        self.lon.setGeometry(QtCore.QRect(0, 40, 579, 16))
        self.lon.setObjectName(_fromUtf8("lon"))
        self.speed = QtGui.QLabel(self.groupBox)
        self.speed.setGeometry(QtCore.QRect(0, 80, 579, 16))
        self.speed.setObjectName(_fromUtf8("speed"))
        self.layoutWidget = QtGui.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(270, 20, 218, 62))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(Video_UAV_Tracker)
        QtCore.QMetaObject.connectSlotsByName(Video_UAV_Tracker)

    def retranslateUi(self, Video_UAV_Tracker):
        Video_UAV_Tracker.setWindowTitle(_translate("Video_UAV_Tracker", "Video UAV Tracker", None))
        self.replayPosition_label.setText(_translate("Video_UAV_Tracker", "-:- / -:-", None))
        self.replay_mapTool_pushButton.setText(_translate("Video_UAV_Tracker", "Map tool", None))
        self.replayPlay_pushButton.setText(_translate("Video_UAV_Tracker", "Play/Pause", None))
        self.sourceLoad_pushButton.setText(_translate("Video_UAV_Tracker", "Open...", None))
        self.time.setText(QtGui.QApplication.translate("Video_UAV_Tracker", "Gps Time:", None, QtGui.QApplication.UnicodeUTF8))
        self.lat.setText(QtGui.QApplication.translate("Video_UAV_Tracker", "Latitude:", None, QtGui.QApplication.UnicodeUTF8))
        self.lon.setText(QtGui.QApplication.translate("Video_UAV_Tracker", "Longitude:", None, QtGui.QApplication.UnicodeUTF8))
        self.ele.setText(QtGui.QApplication.translate("Video_UAV_Tracker", "Elevation:", None, QtGui.QApplication.UnicodeUTF8))
        self.speed.setText(QtGui.QApplication.translate("Video_UAV_Tracker", "Speed:", None, QtGui.QApplication.UnicodeUTF8))
        #self.adactProj.setText(QtGui.QApplication.translate("Video_UAV_Tracker", "adact to EPSG 3857", None, QtGui.QApplication.UnicodeUTF8))


import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Video_UAV_Tracker = QtGui.QWidget()
    ui = Ui_Video_UAV_Tracker()
    ui.setupUi(Video_UAV_Tracker)
    Video_UAV_Tracker.show()
    sys.exit(app.exec_())

