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
				
# wait 
ViewClient.sleep(3)

# close the app
device.shell('am force-stop com.whatsapp')

