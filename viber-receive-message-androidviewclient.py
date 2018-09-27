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
package = 'com.viber.voip'

# set a variable with the name of an Activity in the package
activity = '.WelcomeActivity'

# set the name of the component to start
runComponent = package + '/' + activity

# run the component
device.startActivity(component=runComponent)

vc.dump(window='-1')

try:
	# find a view by id
	com_viber_voip___id_unread_messages_count = vc.findViewByIdOrRaise("com.viber.voip:id/unread_messages_count")
	if com_viber_voip___id_unread_messages_count:

		# click the view
		com_viber_voip___id_subject = vc.findViewByIdOrRaise("com.viber.voip:id/subject")
		com_viber_voip___id_subject.touch()
		vc.dump(window='0')

		com_viber_voip___id_send_text = vc.findViewByIdOrRaise("com.viber.voip:id/send_text")
		if com_viber_voip___id_send_text:
			com_viber_voip___id_send_text.touch()
	
			print "typing..."

			# type in a device
			device.type('Test')
			vc.dump()
			com_viber_voip___id_btn_send = vc.findViewByIdOrRaise("com.viber.voip:id/btn_send")
			if com_viber_voip___id_btn_send:
				
				# send the text 
				com_viber_voip___id_btn_send.touch()
				print "sending....."
			
				# wait 
				ViewClient.sleep(3)


except Exception:
	print "View not found, no new message..."

# close the app
device.shell('am force-stop com.viber.voip')

