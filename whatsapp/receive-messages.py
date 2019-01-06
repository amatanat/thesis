#! /usr/bin/env python
# -*- coding: utf-8 -*-

from com.dtmilano.android.viewclient import ViewClient
import logging
import logging.config
import time
import sys

def get_previous_view_unique_id (unique_id):
	unique_id = unique_id.split("/")
	return unique_id[0] + "/" + unique_id[1] + "/" + str(int(unique_id[2])-1)

def find_message_type (dump, view_id):
	for v in dump:
		if v.uniqueId() == view_id:
			# for the photo message the view id before the emoji button is the 'forward' image's id.
			if v['resource-id'] == "com.whatsapp:id/forward":
				logger.info('last received message is a photo',extra=get_extra_data())
			else:
				logger.info('last received message is a text',extra=get_extra_data())

def get_device_time ():
	import time
	ts = device.shell("echo $EPOCHREALTIME")
	return time.strftime("%F %T",time.gmtime(float(ts)))

def get_extra_data ():
	return {'datetime': get_device_time(), 'version': app_version, 'action': 'receive-message'}

device, serialno = ViewClient.connectToDeviceOrExit(serialno = sys.argv[1])
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

ViewClient.sleep(10)
dump=vc.dump()
for view in dump:
	if view['resource-id'] == "com.whatsapp:id/conversations_row_message_count":
		view.touch()
		logger.info('click new message received conversation',extra=get_extra_data())
		view_dump = vc.dump()
		for v in view_dump:
			if v['resource-id'] == "com.whatsapp:id/emoji_picker_btn":
				emoji_button_unique_id = v.uniqueId()
				previous_view_unique_id = get_previous_view_unique_id(emoji_button_unique_id)
				find_message_type(view_dump, previous_view_unique_id)
			
				# Navigate up 
				com_whatsapp___id_back = vc.findViewByIdOrRaise("com.whatsapp:id/back")
				com_whatsapp___id_back.touch()
				logger.info('navigate to main screen',extra=get_extra_data())
				
				# update the dump
				dump = vc.dump()
				break

# close the app
device.shell('am force-stop com.whatsapp')
logger.info('stop the application',extra=get_extra_data())

# remove the app from the recent task list
device.shell('input keyevent KEYCODE_APP_SWITCH')
device.shell('input keyevent DEL')
logger.info('remove an app from the recent list',extra=get_extra_data())
device.shell('input keyevent KEYCODE_HOME')
logger.info('return HOME',extra=get_extra_data())

