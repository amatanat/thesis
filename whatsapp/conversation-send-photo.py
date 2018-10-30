#! /usr/bin/env python
# -*- coding: utf-8 -*-

from com.dtmilano.android.viewclient import ViewClient
import logging
import logging.config

def get_first_contact_unique_id (unique_id):
	unique_id = unique_id.split("/")
	return unique_id[0] + "/" + unique_id[1] + "/" + str(int(unique_id[2])+5)

device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device,serialno)

app_version = device.shell("dumpsys package com.whatsapp | grep versionName").strip().split("=")[1]
device_time = device.shell("date '+%F %X'").strip()

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('WhatsApp')
d={'datetime': device_time, 'version': app_version, 'action': 'conversation-send-photo'}

# set a variable with the package's internal name
package = 'com.whatsapp'

# set a variable with the name of an Activity in the package
activity = '.Main'

# set the name of the component to start
runComponent = package + '/' + activity

# run the component
device.startActivity(component=runComponent)
logger.info('open application',extra=d)

dump = vc.dump()
try:
	for view in dump:
		if view['resource-id'] == 'android:id/list':
			listview_unique_id = view.uniqueId()
			first_conversation_id = get_first_contact_unique_id(listview_unique_id) 

			for v in dump:
				if v.uniqueId() == first_conversation_id:
					v.touch()
					logger.info('click first conversation',extra=d)

					vc.dump()
					com_whatsapp___id_input_attach_button = vc.findViewByIdOrRaise("com.whatsapp:id/input_attach_button")
					com_whatsapp___id_input_attach_button.touch()
					logger.info('click attachment button',extra=d)
					
		
					vc.dump()
					com_whatsapp___id_pickfiletype_gallery = vc.findViewByIdOrRaise("com.whatsapp:id/pickfiletype_gallery")
					com_whatsapp___id_pickfiletype_gallery.touch()
					logger.info('click Gallery',extra=d)
			
					vc.dump()
					com_whatsapp___id_title = vc.findViewWithTextOrRaise(u'Camera')
					com_whatsapp___id_title.touch()
					logger.info('click Camera folder',extra=d)
			
					vc.dump()
					no_id7 = vc.findViewByIdOrRaise("id/no_id/7")
					no_id7.touch()
					logger.info('select photo',extra=d)
					
					vc.dump()
					com_whatsapp___id_send = vc.findViewByIdOrRaise("com.whatsapp:id/send")
					com_whatsapp___id_send.touch()		
					logger.info('click send button',extra=d)	
				
					# wait 
					ViewClient.sleep(3)
					break
			break
except Exception as e:
	logger.exception('Exception',extra=d)

# close the app
device.shell('am force-stop com.whatsapp')
logger.info('stop the application',extra=d)

# remove the app from the recent task list
device.shell('input keyevent KEYCODE_APP_SWITCH')
device.shell('input keyevent DEL')
logger.info('remove an app from the recent list',extra=d)
device.shell('input keyevent KEYCODE_HOME')
logger.info('return HOME',extra=d)

