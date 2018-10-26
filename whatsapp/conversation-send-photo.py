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

# find an existing conversation by text
com_whatsapp___id_conversations_row_contact_name = vc.findViewWithTextOrRaise(u'Tomi')
if com_whatsapp___id_conversations_row_contact_name:

	print "conversation found..."

	# click the view
	com_whatsapp___id_conversations_row_contact_name.touch()

	vc.dump()
	com_whatsapp___id_input_attach_button = vc.findViewByIdOrRaise("com.whatsapp:id/input_attach_button")
	if com_whatsapp___id_input_attach_button:

		print "attachment touch..." 
		com_whatsapp___id_input_attach_button.touch()
		
		vc.dump()
		com_whatsapp___id_pickfiletype_gallery = vc.findViewByIdOrRaise("com.whatsapp:id/pickfiletype_gallery")
		if com_whatsapp___id_pickfiletype_gallery:

			print "gallery touch..."	
			com_whatsapp___id_pickfiletype_gallery.touch()
			
			vc.dump()
			com_whatsapp___id_title = vc.findViewWithTextOrRaise(u'Camera')
			if com_whatsapp___id_title:
			
				com_whatsapp___id_title.touch()
			
				vc.dump()
				print "Folder 'camera' select..."
				no_id7 = vc.findViewByIdOrRaise("id/no_id/7")
				if no_id7:

					print "Photo selected..."
					no_id7.touch()
					vc.dump()
				
					com_whatsapp___id_send = vc.findViewByIdOrRaise("com.whatsapp:id/send")
					if com_whatsapp___id_send:
				
						print "send photo.."	
						com_whatsapp___id_send.touch()			
				
						# wait 
						ViewClient.sleep(3)

# close the app
device.shell('am force-stop com.whatsapp')

