#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

vc.dump()

# find an existing conversation by text
com_whatsapp___id_conversations_row_contact_name = vc.findViewWithTextOrRaise(u'Tomi')
if com_whatsapp___id_conversations_row_contact_name:

	print "conversation found..."

	# click the view
	com_whatsapp___id_conversations_row_contact_name.touch()

	vc.dump()
	com_whatsapp___id_entry = vc.findViewByIdOrRaise("com.whatsapp:id/entry")
	if com_whatsapp___id_entry:
		com_whatsapp___id_entry.touch()

		print "typing..."

		# type in a device
		device.type('Test')
		vc.dump()
		com_whatsapp___id_send = vc.findViewByIdOrRaise("com.whatsapp:id/send")
		if com_whatsapp___id_send:
				
			# send the text 
			com_whatsapp___id_send.touch()

			print "sending....."
				
			# wait 
			ViewClient.sleep(3)

# close the app
device.shell('am force-stop com.whatsapp')

