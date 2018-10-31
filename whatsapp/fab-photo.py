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
	return {'datetime': get_device_time(), 'version': app_version, 'action': 'fab-photo'}

device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device,serialno)

# get application version and a device time
app_version = device.shell("dumpsys package com.whatsapp | grep versionName").strip().split("=")[1]

# configure logging
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

vc.dump()

try:

	# find a view by id
	com_whatsapp___id_fab = vc.findViewByIdOrRaise("com.whatsapp:id/fab")

	# click the view
	com_whatsapp___id_fab.touch()
	logger.info('click fab',extra=get_extra_data())
	dump = vc.dump()

	for view in dump:
		if view['text'] == "New contact":
			new_contact_unique_id = view.uniqueId()
			first_contact_id = get_first_contact_unique_id(new_contact_unique_id) 

			for v in dump:
				if v.uniqueId() == first_contact_id:
					v.touch()
					logger.info('select first contact',extra=get_extra_data())
					
					vc.dump()
					com_whatsapp___id_input_attach_button = vc.findViewByIdOrRaise("com.whatsapp:id/input_attach_button")
					com_whatsapp___id_input_attach_button.touch()
					logger.info('click attachment button',extra=get_extra_data())
		
					vc.dump()
					com_whatsapp___id_pickfiletype_gallery = vc.findViewByIdOrRaise("com.whatsapp:id/pickfiletype_gallery")
					com_whatsapp___id_pickfiletype_gallery.touch()
					logger.info('click Gallery',extra=get_extra_data())
			
					vc.dump()
					com_whatsapp___id_title = vc.findViewWithTextOrRaise(u'Camera')
					com_whatsapp___id_title.touch()
					logger.info('click Camera folder',extra=get_extra_data())
			
					vc.dump()
					no_id7 = vc.findViewByIdOrRaise("id/no_id/7")
					no_id7.touch()
					logger.info('select photo',extra=get_extra_data())
					
					vc.dump()
					com_whatsapp___id_send = vc.findViewByIdOrRaise("com.whatsapp:id/send")
					com_whatsapp___id_send.touch()	
					logger.info('click send button',extra=get_extra_data())
									
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

