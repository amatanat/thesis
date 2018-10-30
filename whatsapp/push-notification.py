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
d={'datetime': device_time, 'version': app_version, 'action': 'push-notification'}

try:
	# open Navigation bar
	device.dragDip((168.0, 17.0), (184.0, 476.0), 1000, 20, 0)
	logger.info('open Navigation Bar',extra=d)

	dump = vc.dump()
	count = 0
	for v in dump:
		if v.package() == "com.whatsapp":
			# A user received only one text message from a Contact
			if v['resource-id'] == "android:id/big_text": 
				logger.info('A user received a new text message',extra=d)
			# A user received multiple messages from a Contact
			elif v['resource-id'].startswith("android:id/inbox_text"):
				count += 1
			# A user received a photo from a Contact
			elif "Photo" in v.text():
				logger.info('A user received a new photo',extra=d)
			# Message from multiple contacts
			elif v['resource-id'] == "android:id/header_text":
				if "messages" and "chats" in v.text():
					logger.info('A user received new messages from multiple contacts',extra=d)
		
	if count > 0:
		logger.info('A user received %d messages',count,extra=d)

except Exception as e:
	logger.exception('Exception',extra=d)

device.shell('input keyevent KEYCODE_HOME')
logger.info('return HOME',extra=d)

