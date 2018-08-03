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

# find a view by id
com_whatsapp___id_fab = vc.findViewByIdOrRaise("com.whatsapp:id/fab")
if com_whatsapp___id_fab:

	# click the view
	com_whatsapp___id_fab.touch()
	vc.dump(window='0')

	# find a Contact by its text
	com_whatsapp___id_contactpicker_row_name = vc.findViewWithTextOrRaise(u'Tomi')
	if com_whatsapp___id_contactpicker_row_name:
		com_whatsapp___id_contactpicker_row_name.touch()

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

