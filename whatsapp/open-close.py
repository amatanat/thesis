#! /usr/bin/env python
# -*- coding: utf-8 -*-

from com.dtmilano.android.viewclient import ViewClient
import logging
import logging.config
from datetime import datetime

def get_device_time ():
	import time
	ts = device.shell("echo $EPOCHREALTIME")
	return datetime.fromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S')

def get_extra_data ():
	return {'datetime': get_device_time(), 'version': app_version, 'action': 'open-close'}

device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device,serialno)

app_version = device.shell("dumpsys package com.whatsapp | grep versionName").strip().split("=")[1]

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('WhatsApp')

# set a variable with the package's internal name
package = 'com.whatsapp'

# set a variable with the name of an Activity in the package
activity = '.Main'

# set the name of the component to start
runComponent = package + '/' + activity

# run the component
device.startActivity(component=runComponent)
logger.info('open application',extra=get_extra_data())
				
# wait 
ViewClient.sleep(5)

# close the app
device.shell('am force-stop com.whatsapp')
logger.info('stop the application',extra=get_extra_data())

# remove the app from the recent task list
device.shell('input keyevent KEYCODE_APP_SWITCH')
device.shell('input keyevent DEL')
logger.info('remove an app from the recent list',extra=get_extra_data())
device.shell('input keyevent KEYCODE_HOME')
logger.info('return HOME',extra=get_extra_data())

