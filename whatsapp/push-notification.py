#! /usr/bin/env python
# -*- coding: utf-8 -*-

from com.dtmilano.android.viewclient import ViewClient

device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device,serialno)

# open Navigation bar
device.dragDip((168.0, 17.0), (184.0, 476.0), 1000, 20, 0)
dump = vc.dump()
count = 0
for v in dump:
	if v.package() == "com.whatsapp":
		# A user received only one text message from a Contact
		if v['resource-id'] == "android:id/big_text": 
			print "A user received a new text message."
		# A user received multiple messages from a Contact
        	elif v['resource-id'].startswith("android:id/inbox_text"):
			count += 1
		# A user received a photo from a Contact
		elif "Photo" in v.text():
			print "A user received a new photo"
		# Message from multiple contacts
		elif v['resource-id'] == "android:id/header_text":
			if "messages" and "chats" in v.text():
				print "A user received new messages from multiple contacts."
		
if count > 0:
	print "A user received", count, "messages."
	

