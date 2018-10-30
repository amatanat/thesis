#! /usr/bin/env python
# -*- coding: utf-8 -*-

from com.dtmilano.android.viewclient import ViewClient
import logging
import logging.config
import time

def get_previous_view_unique_id (unique_id):
	unique_id = unique_id.split("/")
	return unique_id[0] + "/" + unique_id[1] + "/" + str(int(unique_id[2])-1)

def find_message_type (dump, view_id):
	for v in dump:
		if v.uniqueId() == view_id:
			# for the photo message the view id before the emoji button is the 'forward' image's id.
			if v['resource-id'] == "com.whatsapp:id/forward":
				logger.info('last received message is a photo',extra=d)
			else:
				logger.info('last received message is a text',extra=d)

def get_device_time(ts):
	return time.strftime("%FT%TZ",time.gmtime(ts))

device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device,serialno)

app_version = device.shell("dumpsys package com.whatsapp | grep versionName").strip().split("=")[1]
device_time = device.shell("date '+%F %X'").strip()
#get_device_time(device.shell("echo $EPOCHREALTIME"))

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('WhatsApp')
d={'datetime': device_time, 'version': app_version, 'action': 'receive-message'}

# set a variable with the package's internal name
package = 'com.whatsapp'

# set a variable with the name of an Activity in the package
activity = '.Main'

# set the name of the component to start
runComponent = package + '/' + activity

# run the component
device.startActivity(component=runComponent)
logger.info('open application',extra=d)

dump=vc.dump()
for view in dump:
	if view['resource-id'] == "com.whatsapp:id/conversations_row_message_count":
		view.touch()
		logger.info('click new message received conversation',extra=d)
		view_dump = vc.dump()
		for v in view_dump:
			if v['resource-id'] == "com.whatsapp:id/emoji_picker_btn":
				emoji_button_unique_id = v.uniqueId()
				previous_view_unique_id = get_previous_view_unique_id(emoji_button_unique_id)
				find_message_type(view_dump, previous_view_unique_id)
			
				# Navigate up 
				com_whatsapp___id_back = vc.findViewByIdOrRaise("com.whatsapp:id/back")
				com_whatsapp___id_back.touch()
				logger.info('navigate to main screen',extra=d)
				
				# update the dump
				dump = vc.dump()
				break

# close the app
device.shell('am force-stop com.whatsapp')
logger.info('stop the application',extra=d)

# remove the app from the recent task list
device.shell('input keyevent KEYCODE_APP_SWITCH')
device.shell('input keyevent DEL')
logger.info('remove an app from the recent list',extra=d)
device.shell('input keyevent KEYCODE_HOME')
logger.info('return HOME',extra=d)

