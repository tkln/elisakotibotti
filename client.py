#!/usr/bin/python2
import socket
import pygame
import time
from math import sin, cos, pi

SERVER_IP = '192.168.100.1'
SERVER_PORT = 1337

SCREEN_WIDTH = 150
SCREEN_HEIGHT = 150

JOYSTICK_ID = 0
JOYSTICK_AXIS_A = 3
JOYSTICK_AXIS_B = 4

pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_center = [screen.get_size()[0] / 2, screen.get_size()[1] / 2]
joystick = pygame.joystick.Joystick(JOYSTICK_ID)
joystick.init()

print("connecting to server...")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, SERVER_PORT))

def shift_coord(in_coord):
	ret = [0, 0]
	coord = [0, 0]
	coord[0] = -in_coord[0] + screen.get_size()[0] / 2
	coord[1] = in_coord[1] - screen.get_size()[1] / 2
	ret[0] = coord[0] * cos(pi * 5 / 4) - coord[1] * sin(pi * 5 / 4)
	ret[1] = coord[1] * cos(pi  * 5 / 4) + coord[0] * sin(pi * 5 / 4)
	#print("orig coord: " + int(in_coord) + " to : " + int(ret))
	return ret
def draw_motor_bars(m0, m1):
	if m0 != 7:
		pygame.draw.rect(screen, (0, 255, 0), 
		(0, screen_center[1], screen_center[0],
		(m0 / 7.0) * screen_center[1]))
	if m1 != 7:
		pygame.draw.rect(screen, (0, 255, 0), 
		(screen_center[0], screen_center[1], screen_center[0],
		(-m1 / 7.0) * screen_center[1]))

def set_motors(m0, m1):
	screen.fill((0xff, 0xff, 0xff))
	print("m0: " + str(m0) + " m1: " + str(m1))
	s.send(chr(0x0f & int(m0)))
	s.send(chr((0x0f & int(m1)) | 0x10))
	draw_motor_bars(m0, m1)
	return
def send_mouse():
	print(pygame.mouse.get_pos())
	if shift:
		coord = shift_coord(pygame.mouse.get_pos())
	else:
		coord = [pygame.mouse.get_pos()[0] - screen.get_size()[0] / 2, 
			pygame.mouse.get_pos()[1] - screen.get_size()[1] / 2]
	motor_0_val = (16 * float(coord[0])/screen.get_size()[0])
	motor_1_val = (16 * float(coord[1])/screen.get_size()[1])
	set_motors(motor_0_val, motor_1_val)
def send_joystick():
	if shift:
		coord = shift_coord([joystick.get_axis(JOYSTICK_AXIS_A), 
			joystick.get_axis(JOYSTICK_AXIS_B) + 106.00])
	else:
		coord = [joystick.get_axis(JOYSTICK_AXIS_A), 
			joystick.get_axis(JOYSTICK_AXIS_B) + 106.08]
	motor_0_val = int(7 * coord[0])
	motor_1_val = int(7 * coord[1])
	set_motors(motor_0_val, motor_1_val)

def stop():
	set_motors(7, 7)

shift = True
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
