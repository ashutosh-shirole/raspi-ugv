#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import SocketServer
import wiringpi2 as wiringpi

DRIVE_1 = 7
DRIVE_2 = 1
DRIVE_3 = 10
DRIVE_4 = 11

wiringpi.wiringPiSetup()
wiringpi.softPwmCreate(DRIVE_1, 0, 100)
wiringpi.softPwmWrite(DRIVE_1, 0)
wiringpi.softPwmCreate(DRIVE_2, 0, 100)
wiringpi.softPwmWrite(DRIVE_2, 0)
wiringpi.softPwmCreate(DRIVE_3, 0, 100)
wiringpi.softPwmWrite(DRIVE_3, 0)
wiringpi.softPwmCreate(DRIVE_4, 0, 100)
wiringpi.softPwmWrite(DRIVE_4, 0)

# Map of drives to pins
lDrives = [DRIVE_1, DRIVE_2, DRIVE_3, DRIVE_4]

# Function to set all drives off
def MotorOff():
        wiringpi.softPwmWrite(DRIVE_1, 0)
        wiringpi.softPwmWrite(DRIVE_2, 0)
        wiringpi.softPwmWrite(DRIVE_3, 0)
        wiringpi.softPwmWrite(DRIVE_4, 0)

# Settings for the RemoteKeyBorg server
portListen = 9038                       # What messages to listen for (LEDB on an LCD)

# Class used to handle UDP messages
class PicoBorgHandler(SocketServer.BaseRequestHandler):
    # Function called when a new message has been received
    def handle(self):
        global isRunning

        request, socket = self.request          # Read who spoke to us and what they said
        request = request.upper()               # Convert command to upper case
        driveCommands = request.split(',')      # Separate the command into individual drives
        print 'abc: %s' % (driveCommands)
        if len(driveCommands) == 1:
            # Special commands
            if request == 'ALLOFF':
                # Turn all drives off
                MotorOff()
                print 'All drives off'
            elif request == 'EXIT':
                # Exit the program
                isRunning = False
            else:
                # Unknown command
                print 'Special command "%s" not recognised' % (request)
        elif len(driveCommands) == 2:
                leftVal = driveCommands[0]
                rightVal = driveCommands[1]
                ileftVal = int(leftVal)
                irightVal = int(rightVal)
                print ileftVal
                print irightVal
                wiringpi.softPwmWrite(DRIVE_2, ileftVal)
                wiringpi.softPwmWrite(DRIVE_3, irightVal)
        else:
            # Did not get the right number of drive commands
            print 'Command "%s" did not have %d parts!' % (request, len(lDrives))

try:
    global isRunning
    MotorOff()
    remoteKeyBorgServer = SocketServer.UDPServer(('', portListen), PicoBorgHandler)
    # Loop until terminated remotely
    isRunning = True
    while isRunning:
        remoteKeyBorgServer.handle_request()
    # Turn off the drives and release the GPIO pins
    print 'Finished'
    MotorOff()
except KeyboardInterrupt:
    # CTRL+C exit, turn off the drives and release the GPIO pins
    print 'Terminated'
    MotorOff()
