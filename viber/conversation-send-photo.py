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

# find a conversation by a Contact's name
com_viber_voip___id_from = vc.findViewWithTextOrRaise(u'Tomi')
if com_viber_voip___id_from:

	com_viber_voip___id_from.touch()
	vc.dump()

	# open gallery
	com_viber_voip___id_options_menu_open_gallery = vc.findViewByIdOrRaise("com.viber.voip:id/options_menu_open_gallery")
	if com_viber_voip___id_options_menu_open_gallery:

		com_viber_voip___id_options_menu_open_gallery.touch()
		print "options menu open gallery..."
		vc.dump()
			
		# find the photo			
		com_viber_voip___id_image = vc.findViewByIdOrRaise("com.viber.voip:id/image")
		if com_viber_voip___id_image:
			com_viber_voip___id_image.touch()
			print "select a photo..."
			vc.dump()
	
			# send a photo
			com_viber_voip___id_btn_send = vc.findViewByIdOrRaise("com.viber.voip:id/btn_send")
			if com_viber_voip___id_btn_send:
				com_viber_voip___id_btn_send.touch()
				print "send a photo..."

				# wait 
				ViewClient.sleep(3)

# close the app
device.shell('am force-stop com.viber.voip')

