#!/usr/bin/python2
import socket
import pygame
import time
import sys
from math import sin, cos, pi

#SERVER_IP = '192.168.100.1'
SERVER_IP = '192.168.1.100'
SERVER_PORT = 1337

SCREEN_WIDTH = 200
SCREEN_HEIGHT = 200

#used for mouse scaling and mirroring
MCAL = [-1, 1]

#bar graph scalers
B0M = 1
#the other motor is reversed
B1M = -1

JOY_ID = 0
JOY_AXIS_A = 3
JOY_AXIS_B = 4
JOY_AXIS_TA = 1
JOY_AXIS_TB = 4
JCAL = [1.5, 1.5]

COORD_ANGL = pi * 5 / 4 

#motor scalers
MSCALE = [7, 7]

keymap = { 
	'u' : (1.0, 1.0),
	'ul' : (0.5, 1.0),
	'ur' : (1.0, 0.5),
	'd' : (-1.0, -1.0),
	'dl' : (-0.5, -1.0),
	'dr' : (-1.0, -0.5),
	'l' : (1.0, -1.0),
	'r' : (-1.0, 1.0)
}
	

def tuple_mul(a, b):
	return (a[0] * b[0], a[1] * b[1])

def rotate_coord(coord):
	ret = [0, 0]
	ret[0] = coord[0] * cos(COORD_ANGL) - coord[1] * sin(COORD_ANGL)
	ret[1] = coord[1] * cos(COORD_ANGL) + coord[0] * sin(COORD_ANGL)
	#print("orig coord: " + int(in_coord) + " to : " + int(ret))
	return ret

def draw_motor_bars(m0, m1):
	screen.fill((0xff, 0xff, 0xff))
	if m0 != 7:
		pygame.draw.rect(screen, (0, 255, 0), 
		(0, screen_center[1], screen_center[0],
		(B0M * m0 / 7.0) * screen_center[1]))
	if m1 != 7:
		pygame.draw.rect(screen, (0, 255, 0), 
		(screen_center[0], screen_center[1], screen_center[0],
		(B1M * m1 / 7.0) * screen_center[1]))

def set_motors(m0, m1):
	#values less than 7 are reverse
	#value clamping to prevent overflows
	print(m0)
	print(m1)
	if m0 > 1.0:
		m0 = .99
	if m0 < -1.0:
		m0 = -0.99
	if m1 > 1.0:
		m1 = 0.99
	if m1 < -1.0:
		m1 = -0.99
	print(m0)
	print(m1)
	transmit_motors(m0 * 7, m1 * 7)
	
def transmit_motors(m0, m1):
	print("m0: " + str(int(m0) & 0x0f) + " m1: " + str(int(m1) & 0x0f))
	try:	
		s.send(chr(0x0f & int(m0)))
		s.send(chr((0x0f & int(m1)) | 0x10))
	except socket.error:
		print("Failed to transmit motor commands!")
	draw_motor_bars(m0, m1)

def send_mouse():
	coord = [pygame.mouse.get_pos()[0] - screen.get_size()[0] / 2, 
		pygame.mouse.get_pos()[1] - screen.get_size()[1] / 2]

	if not tankdrive:
		coord = rotate_coord(coord)
	set_motors(1.5 * coord[0]/screen.get_width(), 1.5 * coord[1]/screen.get_height())

def send_joystick():
	if not tankdrive:
		coord = rotate_coord((joystick.get_axis(JOY_AXIS_A) * JCAL[0], 
				joystick.get_axis(JOY_AXIS_B) * JCAL[1]))
	else:
		coord = [joystick.get_axis(JOY_AXIS_A) + 1.0, 
			joystick.get_axis(JOY_AXIS_B) + 1.0]
	print(coord)
	print(coord)
	motor_0_val = (18 * float(coord[0]))
	motor_1_val = (18 * float(coord[1]))
	#transmit_motors(motor_0_val, motor_1_val)
	set_motors(coord[0], coord[1])
	pygame.draw.line(screen, (255, 0, 0), 
	screen_center, (((joystick.get_axis(JOY_AXIS_A)) + 1.0 ) * screen_center[0],
                         ((joystick.get_axis(JOY_AXIS_B)) + 1.0 ) * screen_center[1]))

def send_keys():
	pressed_keys = pygame.key.get_pressed()
	print(pressed_keys[pygame.K_LEFT])	
	key_coords = [0, 0]
	if pressed_keys[pygame.K_UP]:	
		key_coords[1] = -1.5
	elif pressed_keys[pygame.K_DOWN]:
		key_coords[1] = 1.5
	if pressed_keys[pygame.K_LEFT]:	
		key_coords[0] = -1.5
	elif pressed_keys[pygame.K_RIGHT]:
		key_coords[0] = 1.5
	set_motors(rotate_coord(key_coords)[0], rotate_coord(key_coords)[1])

def motors_stop():
	transmit_motors(7, 7)
#Inits
pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_center = [screen.get_size()[0] / 2, screen.get_size()[1] / 2]

try:
	joystick = pygame.joystick.Joystick(JOY_ID)
	joystick.init()
except pygame.error:
	print("No joystick found.")

print("Connecting to the server: " + SERVER_IP + ":" + str(SERVER_PORT))

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((SERVER_IP, SERVER_PORT))
except socket.error:
	print("Unable to connect to the server ")


tankdrive = False
running = True
motors_stop()
screen.fill((0xff, 0xff, 0xff))
while running:
	event = pygame.event.poll()
	if event.type == pygame.QUIT:
		motors_stop()
		running = False
	elif event.type == pygame.MOUSEMOTION:
		if pygame.mouse.get_pressed()[0]:
			send_mouse()
			pygame.draw.line(screen, (255, 0, 0), 
				screen_center, pygame.mouse.get_pos())
	elif event.type == pygame.MOUSEBUTTONUP:
		motors_stop()
	elif event.type == pygame.JOYAXISMOTION:
		send_joystick()
	elif event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
		send_keys()	
	
	pygame.display.flip()
	time.sleep(0.02)
s.close()
