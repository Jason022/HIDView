#! python2
#coding: utf-8
import os
import sys
import threading
import ConfigParser

import sip
sip.setapi('QString', 2)
from PyQt4 import QtCore, QtGui, uic

from interface import USB_BACKEND

import codec


'''
from HIDView_UI import Ui_HIDView
class HIDView(QtGui.QWidget, Ui_HIDView):
    def __init__(self, parent=None):
        super(HIDView, self).__init__(parent)
        
        self.setupUi(self)
'''
class HIDView(QtGui.QWidget):
    def __init__(self, parent=None):
        super(HIDView, self).__init__(parent)
        
        uic.loadUi('HIDView.ui', self)

        devices = USB_BACKEND.get_all_connected_interfaces()
        self.devices = {dev.info(): dev for dev in devices}
        self.cmbPort.addItems(self.devices.keys())

        self.cmbCode.addItems(codec.Codecs.keys())

        self.initSetting()

        self.tmrHID = QtCore.QTimer()
        self.tmrHID.setInterval(10)
        self.tmrHID.timeout.connect(self.on_tmrHID_timeout)
        self.tmrHID.start()
    
    def initSetting(self):
        if not os.path.exists('setting.ini'):
            open('setting.ini', 'w')
        
        self.conf = ConfigParser.ConfigParser()
        self.conf.read('setting.ini')
        
        if not self.conf.has_section('device'):
            self.conf.add_section('device')
            self.conf.set('device', 'port', '')

            self.conf.add_section('codec')
            self.conf.set('codec', 'name', 'None')

            self.conf.add_section('history')
            self.conf.set('history', 'hist1', '')
            self.conf.set('history', 'hist2', '')

        index = self.cmbPort.findText(self.conf.get('device', 'port').decode('gbk'))
        self.cmbPort.setCurrentIndex(index if index != -1 else 0)

        self.cmbCode.setCurrentIndex(self.cmbCode.findText(self.conf.get('codec', 'name')))

        self.txtSend.setPlainText(self.conf.get('history', 'hist1').decode('gbk'))

    @QtCore.pyqtSlot()
    def on_btnOpen_clicked(self):
        if self.btnOpen.text() == u'打开连接':
            try:
                self.dev = self.devices[self.cmbPort.currentText()]
                self.dev.open()
            except Exception as e:
                print e
            else:
                self.cmbPort.setEnabled(False)
                self.btnOpen.setText(u'断开连接')
        else:
            self.dev.close()

            self.cmbPort.setEnabled(True)
            self.btnOpen.setText(u'打开连接')

    @QtCore.pyqtSlot()
    def on_btnSend_clicked(self):
        if self.btnOpen.text() == u'断开连接':
            text = self.txtSend.toPlainText()

            self.codec.send(text)
        else:
            self.txtMain.append(u'\n请先打开连接\n')

    def on_tmrHID_timeout(self):
        if self.btnOpen.text() == u'断开连接':
            list = self.dev.read()
            if list:
                self.codec.recv(list)
        
        else:
            devices = USB_BACKEND.get_all_connected_interfaces()
            devices = {dev.info(): dev for dev in devices}
            if len(devices) != self.cmbPort.count():
                self.devices = devices
                self.cmbPort.clear()
                self.cmbPort.addItems(devices.keys())

    @QtCore.pyqtSlot(str)
    def on_cmbCode_currentIndexChanged(self, text):
        self.codec = codec.Codecs[text](self)
        
        self.codec.info()

    @QtCore.pyqtSlot()
    def on_btnClear_clicked(self):
        self.txtMain.clear()
    
    def closeEvent(self, evt):
        self.conf.set('codec', 'name', self.cmbCode.currentText())
        self.conf.set('device', 'port', self.cmbPort.currentText().encode('gbk'))
        self.conf.set('history', 'hist1', self.txtSend.toPlainText().encode('gbk'))
        self.conf.write(open('setting.ini', 'w'))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    hid = HIDView()
    hid.show()
    sys.exit(app.exec_())
