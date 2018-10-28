#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import os

from com.dtmilano.android.viewclient import ViewClient

def get_previous_view_unique_id (unique_id):
	unique_id = unique_id.split("/")
	return unique_id[0] + "/" + unique_id[1] + "/" + str(int(unique_id[2])-1)

def find_message_type (dump, view_id):
	for v in dump:
		if v.uniqueId() == view_id:
			# for the photo message the view id before the emoji button is the 'forward' image's id.
			if v['resource-id'] == "com.whatsapp:id/forward":
				print "last message is a photo."
			else:
				print "last message is a text."

device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device,serialno)

print "launching app..."

# set a variable with the package's internal name
package = 'com.whatsapp'

# set a variable with the name of an Activity in the package
activity = '.Main'

# set the name of the component to start
runComponent = package + '/' + activity

# run the component
device.startActivity(component=runComponent)

dump=vc.dump()
for view in dump:
	if view['resource-id'] == "com.whatsapp:id/conversations_row_message_count":
		view.touch()
		view_dump = vc.dump()
		for v in view_dump:
			if v['resource-id'] == "com.whatsapp:id/emoji_picker_btn":
				emoji_button_unique_id = v.uniqueId()
				previous_view_unique_id = get_previous_view_unique_id(emoji_button_unique_id)
				find_message_type(view_dump, previous_view_unique_id)
			
				# Navigate up 
				com_whatsapp___id_back = vc.findViewByIdOrRaise("com.whatsapp:id/back")
				com_whatsapp___id_back.touch()
				
				# update the dump
				dump = vc.dump()
				break
# close the app
device.shell('am force-stop com.whatsapp')

