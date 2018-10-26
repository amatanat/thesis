#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import os

from com.dtmilano.android.viewclient import ViewClient

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

vc.dump(window='-1')

# new message check
com_whatsapp___id_conversations_row_message_count = vc.findViewByIdOrRaise("com.whatsapp:id/conversations_row_message_count")
if com_whatsapp___id_conversations_row_message_count:

	print "new message found..."

	com_whatsapp___id_single_msg_tv = vc.findViewWithTextOrRaise(u'Photo')
	if com_whatsapp___id_single_msg_tv:
		
		print "new message is a photo..."
		com_whatsapp___id_single_msg_tv.touch()

	else:
		print "new message is a text..."
		com_whatsapp___id_conversations_row_message_count.touch()
		
	print "read a new message..."
				
	# wait 
	ViewClient.sleep(3)

# close the app
device.shell('am force-stop com.whatsapp')

