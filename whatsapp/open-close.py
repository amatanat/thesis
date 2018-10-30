#! /usr/bin/env python
# -*- coding: utf-8 -*-

from com.dtmilano.android.viewclient import ViewClient
import logging
import logging.config

device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device,serialno)

app_version = device.shell("dumpsys package com.whatsapp | grep versionName").strip().split("=")[1]
device_time = device.shell("date '+%F %X'").strip()

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('WhatsApp')
d={'datetime': device_time, 'version': app_version, 'action': 'open-close'}

# set a variable with the package's internal name
package = 'com.whatsapp'

# set a variable with the name of an Activity in the package
activity = '.Main'

# set the name of the component to start
runComponent = package + '/' + activity

# run the component
device.startActivity(component=runComponent)
logger.info('open application',extra=d)
				
# wait 
ViewClient.sleep(3)

# close the app
device.shell('am force-stop com.whatsapp')
logger.info('stop the application',extra=d)

# remove the app from the recent task list
device.shell('input keyevent KEYCODE_APP_SWITCH')
device.shell('input keyevent DEL')
logger.info('remove an app from the recent list',extra=d)
device.shell('input keyevent KEYCODE_HOME')
logger.info('return HOME',extra=d)

