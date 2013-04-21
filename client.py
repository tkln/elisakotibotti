#!/usr/bin/python2
import socket
import pygame
import math
from math import sin, cos, pi

pygame.init()
screen = pygame.display.set_mode((150, 150))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.100.1', 1337))

def shift_coord(in_coord):
	ret = [0, 0]
	coord = [0, 0]
	coord[0] = in_coord[1] - screen.get_size[0] / 2
	coord[1] = in_coord[0] - screen.get_size[1] / 2
	ret[0] = int(coord[0] * cos(pi / 4) - coord[1] * sin(pi / 4))
	ret[1] = int(coord[1] * cos(pi / 4) + coord[0] * sin(pi / 4))
	#print("orig coord: " + int(in_coord) + " to : " + int(ret))
	return ret

shift = True

def send_mouse():
	print(pygame.mouse.get_pos())
	if shift:
		coord = shift_coord(pygame.mouse.get_pos())
	else:
		coord = [pygame.mouse.get_pos()[0] - screen.get_size[0] / 2, 
			pygame.mouse.get_pos()[1] - screen.get_size[1] / 2]
	motor_0_val = (14 * coord[0]/screen.get_size()[0])
	motor_1_val = (14 * coord[1]/screen.get_size()[1])
	print("m0 val: " + str(motor_0_val) + " m1 val: " + str(motor_1_val))
	s.send(chr(0x0f & motor_0_val))
	s.send(chr((0x0f & motor_1_val) | 0x10))

def stop():
	s.send('\x07')
	s.send('\x17')

running = True
stop()
screen.fill((0xff, 0xff, 0xff))
pygame.display.flip()
while running:
	event = pygame.event.poll()
	if event.type == pygame.QUIT:
		stop()
		running = False
	elif event.type == pygame.MOUSEMOTION:
		if pygame.mouse.get_pressed()[0]:
			send_mouse()
	elif event.type == pygame.MOUSEBUTTONUP:
		stop()
s.close()
