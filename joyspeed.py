#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import socket
import time
import os
import sys
import pygame

# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
#sys.stdout = sys.stderr


# Settings for the joystick
regularUpdate = True                    # If True we send a command at a regular interval, if False we only send commands when keys are pressed or released
broadcastIP = '192.168.2.5'           # IP address to send to, 255 in one or more positions is a broadcast / wild-card
broadcastPort = 9038                    # What message number to send with
leftDrive = 2                     # Drive number for left motor
rightDrive = 3                    # Drive number for right motor
axisUpDown = 1                          # Joystick axis to read for up / down position
axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
axisLeftRight = 3                       # Joystick axis to read for left / right position
axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
buttonSlow = 6                          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5                        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 7                      # Joystick button number for turning fast (R2)
interval = 0.1                         # Time between updates in seconds, smaller responds faster but uses more processor time
controllerLostLoops = 20                # Number of loops without any joystick events before announcing the joystick as out of range

global hadEvent
global moveUp
global moveDown
global moveLeft
global moveRight
global moveQuit
global speedTurn
global speedDown
global driveLeft
global driveRight
driveLeft = 0.0
driveRight = 0.0
hadEvent = True
moveUp = False
moveDown = False
moveLeft = False
moveRight = False
moveQuit = False
speedTurn = False
speedDown = False
# Setup the connection for sending on
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)       # Create the socket
sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)                        # Enable broadcasting (sending to many IPs based on wild-cards)
sender.bind(('0.0.0.0', 0))                                                         # Set the IP and port number to use locally, IP 0.0.0.0 means all connections and port 0 means assign a number for us (do not care)

# Setup pygame and wait for the joystick to become available
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(1)
joystick.init()
screen = pygame.display.set_mode([300,300])
pygame.display.set_caption("RemoteKeyBorg - Press [ESC] to quit")

# Function to handle pygame events
def PygameHandler(events):
	# Variables accessible outside this function
	global hadEvent
	global moveUp
	global moveDown
	global moveLeft
	global moveRight
	global moveQuit
	global speedTurn
	global speedDown
	global driveLeft
	global driveRight
	# Handle each event individually
	for event in events:
		if event.type == pygame.QUIT:
			# User exit
			hadEvent = True
			moveQuit = True
		elif event.type == pygame.KEYDOWN:
			# A key has been pressed, see if it is one we want
			hadEvent = True
			if event.key == pygame.K_ESCAPE:
				moveQuit = True
		elif event.type == pygame.KEYUP:
			# A key has been released, see if it is one we want
			hadEvent = True
			if event.key == pygame.K_ESCAPE:
				moveQuit = False
		elif event.type == pygame.JOYAXISMOTION:
			# A joystick has been moved, read axis positions (-1 to +1)
			hadEvent = True
			upDown = joystick.get_axis(axisUpDown)
			leftRight = joystick.get_axis(axisLeftRight)
			# Invert any axes which are incorrect
			if axisUpDownInverted:
				upDown = -upDown
			if axisLeftRightInverted:
				leftRight = -leftRight
			# Determine Up / Down values
			driveLeft = -upDown
	                driveRight = -upDown
			if upDown < -0.1:
				moveUp = True
				moveDown = False
			elif upDown > 0.1:
				moveUp = False
				moveDown = True
			else:
				moveUp = False
				moveDown = False
			# Determine Left / Right values
			if leftRight < -0.2:
				driveLeft *= 1.0 + (2.0 * leftRight)
			elif leftRight > 0.2:
				driveRight *= 1.0 - (2.0 * leftRight)
			else:
				moveLeft = False
				moveRight = False

try:
	print 'Press CTRL+C to quit'
	running = True	
	loopsWithoutEvent = 0
	controllerLost = False	
	# Loop indefinitely
	while running:
		PygameHandler(pygame.event.get())
		#print 'event handled'
		if hadEvent or regularUpdate:				
			# Check for button presses
			if joystick.get_button(buttonSlow):
				driveLeft *= slowFactor
				driveRight *= slowFactor                
			idriveLeft = int(driveLeft * 100)
			if idriveLeft < 0:
				# Cannot reverse, go to stopped
				idriveLeft = 0
			elif idriveLeft > 100:
				# Beyond full speed, go to full speed
				idriveLeft = 100
			idriveRight = int(driveRight * 100)
			if idriveRight < 0:
				# Cannot reverse, go to stopped
				idriveRight = 0
			elif idriveRight > 100:
				# Beyond full speed, go to full speed
				idriveRight = 100
			if joystick.get_button(buttonFastTurn):
				break
			command = ''
			command = '' + `idriveRight` + ',' + `idriveLeft`
			sender.sendto(command, (broadcastIP, broadcastPort))
		time.sleep(interval)
	sender.sendto('ALLOFF', (broadcastIP, broadcastPort))
except KeyboardInterrupt:
	print '\nUser shutdown'
	sender.sendto('ALLOFF', (broadcastIP, broadcastPort))