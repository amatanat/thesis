#! /usr/bin/env python
# -*- coding: utf-8 -*-

from com.dtmilano.android.viewclient import ViewClient
import logging
import logging.config

def get_device_time ():
	return device.shell("date '+%F %X'").strip()

def get_extra_data ():
	return {'datetime': get_device_time(), 'version': app_version, 'action': 'push-notification'}

device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device,serialno)

app_version = device.shell("dumpsys package com.whatsapp | grep versionName").strip().split("=")[1]

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('WhatsApp')

try:
	# open Navigation bar
	device.dragDip((168.0, 17.0), (184.0, 476.0), 1000, 20, 0)
	logger.info('open Navigation Bar',extra=get_extra_data())

	dump = vc.dump()
	count = 0
	for v in dump:
		if v.package() == "com.whatsapp":
			# A user received only one text message from a Contact
			if v['resource-id'] == "android:id/big_text": 
				logger.info('A user received a new text message',extra=get_extra_data())
			# A user received multiple messages from a Contact
			elif v['resource-id'].startswith("android:id/inbox_text"):
				count += 1
			# A user received a photo from a Contact
			elif "Photo" in v.text():
				logger.info('A user received a new photo',extra=get_extra_data())
			# Message from multiple contacts
			elif v['resource-id'] == "android:id/header_text":
				if "messages" and "chats" in v.text():
					logger.info('A user received new messages from multiple contacts',extra=get_extra_data())
		
	if count > 0:
		logger.info('A user received %d messages',count,extra=get_extra_data())

except Exception as e:
	logger.exception('Exception',extra=get_extra_data())

device.shell('input keyevent KEYCODE_HOME')
logger.info('return HOME',extra=get_extra_data())

