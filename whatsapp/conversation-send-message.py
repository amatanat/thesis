#! /usr/bin/env python
# -*- coding: utf-8 -*-

from com.dtmilano.android.viewclient import ViewClient
import logging
import logging.config

def get_first_contact_unique_id (unique_id):
	unique_id = unique_id.split("/")
	return unique_id[0] + "/" + unique_id[1] + "/" + str(int(unique_id[2])+5)

def get_device_time ():
	return device.shell("date '+%F %X'").strip()

def get_extra_data ():
	return {'datetime': get_device_time(), 'version': app_version, 'action': 'conversation-send-message'}

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

dump = vc.dump()
try:
	for view in dump:
		if view['resource-id'] == 'android:id/list':
			listview_unique_id = view.uniqueId()
			first_conversation_id = get_first_contact_unique_id(listview_unique_id) 

			for v in dump:
				if v.uniqueId() == first_conversation_id:
					v.touch()
					logger.info('click first conversation',extra=get_extra_data())

					vc.dump()
					com_whatsapp___id_entry = vc.findViewByIdOrRaise("com.whatsapp:id/entry")
					com_whatsapp___id_entry.touch()
					logger.info('click entry',extra=get_extra_data())

					# type in a device
					device.type('Test')
					logger.info('type message',extra=get_extra_data())
		
					vc.dump()
					com_whatsapp___id_send = vc.findViewByIdOrRaise("com.whatsapp:id/send")
					com_whatsapp___id_send.touch()
					logger.info('send message',extra=get_extra_data())
				
					# wait 
					ViewClient.sleep(3)
					break
			break
except Exception as e:
	logger.exception('Exception',extra=get_extra_data())

# close the app
device.shell('am force-stop com.whatsapp')
logger.info('stop the application',extra=get_extra_data())

# remove the app from the recent task list
device.shell('input keyevent KEYCODE_APP_SWITCH')
device.shell('input keyevent DEL')
logger.info('remove an app from the recent list',extra=get_extra_data())
device.shell('input keyevent KEYCODE_HOME')
logger.info('return HOME',extra=get_extra_data())

