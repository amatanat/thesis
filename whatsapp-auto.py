#!/usr/bin/python
# -*- coding: ascii -*-
# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
from com.android.monkeyrunner.easy import EasyMonkeyDevice, By

# Connects to the currently running device, returning a MonkeyDevice object
device = MonkeyRunner.waitForConnection()
easy_device = EasyMonkeyDevice(device)

# Check if WhatsApp is already installed or not
apk_path = device.shell('pm path com.whatsapp')
if apk_path.startswith('package:'):
    print "app already installed."
else:
    print "app not installed, installing APKs..."
    device.installPackage('/home/amatanat/Downloads/WhatsApp.apk')

print "launching app..."

# Installs the Android package. Notice that this method returns a boolean, so you can test
# to see if the installation worked.
#device.installPackage('/home/amatanat/Downloads/WhatsApp.apk')

# sets a variable with the package's internal name
package = 'com.whatsapp'

# sets a variable with the name of an Activity in the package
activity = '.Main'

# sets the name of the component to start
runComponent = package + '/' + activity

# Runs the component
device.startActivity(component=runComponent)

# wait for few seconds
MonkeyRunner.sleep(5)

# press eula button 
#easy_device.touch(By.id('id/eula_accept'), MonkeyDevice.DOWN_AND_UP)
#device.press("DPAD_CENTER",MonkeyDevice.DOWN_AND_UP)
#MonkeyRunner.sleep(5)

result = device.takeSnapshot()
result.writeToFile('/home/amatanat/Desktop/home.png','png')

# Click on FAB button to start a new conversation.
easy_device.touch(By.id('id/fab'), MonkeyDevice.DOWN_AND_UP)
MonkeyRunner.sleep(5)


# Presses the Menu button
#device.press('KEYCODE_MENU', MonkeyDevice.DOWN_AND_UP)

# Takes a screenshot
result = device.takeSnapshot()

# Writes the screenshot to a file
result.writeToFile('/home/amatanat/Desktop/fab.png','png')
