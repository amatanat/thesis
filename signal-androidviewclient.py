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
package = 'org.thoughtcrime.securesms'

# set a variable with the name of an Activity in the package
activity = '.ConversationListActivity'

# set the name of the component to start
runComponent = package + '/' + activity

# run the component
device.startActivity(component=runComponent)

vc.dump(window='-1')

# find a view by id
org_thoughtcrime_securesms___id_fab = vc.findViewByIdOrRaise("org.thoughtcrime.securesms:id/fab")
if org_thoughtcrime_securesms___id_fab:

	# click the view
	org_thoughtcrime_securesms___id_fab.touch()
	vc.dump(window='0')

	# find a Contact by its text
	org_thoughtcrime_securesms___id_name = vc.findViewWithTextOrRaise(u'Tomi')
	if org_thoughtcrime_securesms___id_name:
		org_thoughtcrime_securesms___id_name.touch()

		vc.dump()
		org_thoughtcrime_securesms___id_embedded_text_editor = vc.findViewWithTextOrRaise(u'Signal message')
		if org_thoughtcrime_securesms___id_embedded_text_editor:
			org_thoughtcrime_securesms___id_embedded_text_editor.touch()

			print "typing..."

			# type in a device
			device.type('Test')
			vc.dump()
			org_thoughtcrime_securesms___id_send_button = vc.findViewByIdOrRaise("org.thoughtcrime.securesms:id/send_button")
			if org_thoughtcrime_securesms___id_send_button:
				
				# send the text 
				org_thoughtcrime_securesms___id_send_button.touch()

				print "sending....."
				
				# wait 
				ViewClient.sleep(3)

# close the app
device.shell('am force-stop org.thoughtcrime.securesms')

