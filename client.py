#!/usr/bin/python2
import socket
import pygame
import time
from math import sin, cos, pi

#SERVER_IP = '192.168.100.1'
SERVER_IP = '192.168.1.100'
SERVER_PORT = 1336

SCREEN_WIDTH = 200
SCREEN_HEIGHT = 200

#used for mouse scaling and mirroring
MXM = -1
MYM = 1
MCAL = [-1, 1]

#bar graph scalers
B0M = 1
B1M = -1

JOYSTICK_ID = 0
JOYSTICK_AXIS_A = 3
JOYSTICK_AXIS_B = 4
JOYSTICK_AXIS_TA = 1
JOYSTICK_AXIS_TB = 4

COORD_ANGL = pi * 5 / 4 

pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_center = [screen.get_size()[0] / 2, screen.get_size()[1] / 2]

try:
	joystick = pygame.joystick.Joystick(JOYSTICK_ID)
	joystick.init()
except pygame.error:
	print("No joystick found.")

print("Connecting to the server: " + SERVER_IP + ":" + str(SERVER_PORT))

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((SERVER_IP, SERVER_PORT))
except socket.error:
	print("Unable to connect to the server ")

def tuple_mul(a, b):
	return (a[0] * b[0], a[1] * b[1])

def rotate_coord_u(coord):
	ret = [0, 0]
	ret[0] = coord[0] * cos(COORD_ANGL) - coord[1] * sin(COORD_ANGL)
	ret[1] = coord[1] * cos(COORD_ANGL) + coord[0] * sin(COORD_ANGL)
	#print("orig coord: " + int(in_coord) + " to : " + int(ret))
	return ret

def rotate_mouse_coord(in_coord):
	ret = [0, 0]
	coord = [0, 0]
	#offsets the origo of mouse to the center of the screen	
	#these should go to mouse handling
	coord[0] = in_coord[0] - MCAL[0] * screen.get_size()[0] / 2
	coord[1] = in_coord[1] - MCAL[1] * screen.get_size()[1] / 2
	#the actual coordinate offsetting
	ret = rotate_coord_u(coord)
	#print("orig coord: " + int(in_coord) + " to : " + int(ret))
	return ret

def draw_motor_bars(m0, m1):
	if m0 != 7:
		pygame.draw.rect(screen, (0, 255, 0), 
		(0, screen_center[1], screen_center[0],
		(B0M * m0 / 7.0) * screen_center[1]))
	if m1 != 7:
		pygame.draw.rect(screen, (0, 255, 0), 
		(screen_center[0], screen_center[1], screen_center[0],
		(B1M * m1 / 7.0) * screen_center[1]))

def set_motors(m0, m1):
	screen.fill((0xff, 0xff, 0xff))
	print("m0: " + str(m0) + " m1: " + str(m1))
	try:	
		s.send(chr(0x0f & int(m0)))
		s.send(chr((0x0f & int(m1)) | 0x10))
	except socket.error:
		print("Failed to transmit motor commands!")
	draw_motor_bars(m0, m1)

def send_mouse():
	#print(pygame.mouse.get_pos())
	if not tankdrive:
		coord = rotate_mouse_coord(tuple_mul(pygame.mouse.get_pos(), MCAL))
	else:
		coord = [pygame.mouse.get_pos()[0] - screen.get_size()[0] / 2, 
			pygame.mouse.get_pos()[1] - screen.get_size()[1] / 2]
	motor_0_val = (16 * float(coord[0])/screen.get_size()[0])
	motor_1_val = (16 * float(coord[1])/screen.get_size()[1])
	set_motors(motor_0_val, motor_1_val)

def send_joystick():
	if not tankdrive:
		coord = rotate_mouse_coord(tuple_mul(MCAL, (((joystick.get_axis(JOYSTICK_AXIS_A)) + 1.0 ) * screen_center[0],
                         ((joystick.get_axis(JOYSTICK_AXIS_B)) + 1.0 ) * screen_center[1])))

	else:
		coord = [joystick.get_axis(JOYSTICK_AXIS_A) + 1.0, 
			joystick.get_axis(JOYSTICK_AXIS_B) + 1.0]
	#if coord[0] > 10.0 or coord[0] < 0.1:
	#	coord[0] = 0
	print(coord)
	print(coord)
	motor_0_val = int(16 * float(coord[0]) / screen.get_size()[0])
	motor_1_val = int(16 * float(coord[1]) / screen.get_size()[1])
	if abs(coord[0]) < 0.01:
		motor_0_val = 7;
	if abs(coord[1]) < 0.01:
		motor_1_val = 7
	set_motors(motor_0_val, motor_1_val)
	pygame.draw.line(screen, (255, 0, 0), 
	screen_center, (((joystick.get_axis(JOYSTICK_AXIS_A)) + 1.0 ) * screen_center[0],
                         ((joystick.get_axis(JOYSTICK_AXIS_B)) + 1.0 ) * screen_center[1]))


def stop():
	set_motors(7, 7)

tankdrive = False
running = True
stop()
screen.fill((0xff, 0xff, 0xff))
while running:
	
	event = pygame.event.poll()
	if event.type == pygame.QUIT:
		stop()
		running = False
	elif event.type == pygame.MOUSEMOTION:
		if pygame.mouse.get_pressed()[0]:
			send_mouse()
			pygame.draw.line(screen, (255, 0, 0), 
				screen_center, pygame.mouse.get_pos())
	elif event.type == pygame.MOUSEBUTTONUP:
		stop()
	elif event.type == pygame.JOYAXISMOTION:
		send_joystick()

	pygame.display.flip()
	time.sleep(0.02)
s.close()
