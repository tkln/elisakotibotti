#!/usr/bin/python
#assumnig a system where python version is 2.7
import time
import socket
import thread
import signal
import sys

class Motor:
	speed = 0
	PWM_RATE = 100.0
	LINE_BASE_PATH = '/sys/class/leds/'
	
	def set_a_line(self, state):
		self.hb_a_line_file.seek(0,0)
		self.hb_a_line_file.write(str(state))	
		return
	def set_b_line(self, state):
		self.hb_b_line_file.seek(0,0)	
		self.hb_b_line_file.write(str(state))	
		return
	def __pwm_thread_func(self, arg1, arg2):
		print("motor pwm thread function started")
		while (1):
			time.sleep((8 - abs(self.speed)) / self.PWM_RATE)
			#turn motor on
			if self.speed < 0:
				self.set_a_line(1)
				self.set_b_line(0)
			elif self.speed == 0:
				self.set_a_line(0)
				self.set_b_line(0)
			else:
				self.set_a_line(0)
				self.set_b_line(1)
			time.sleep(abs(self.speed) / self.PWM_RATE)
			#turn motor off
			self.set_a_line(0)
			self.set_b_line(0)
		return
	def __init__(self, a_line, b_line):
		#setup the thread for bitbang pwm
		self.HB_A_LINE = a_line
		self.HB_B_LINE = b_line
		self.hb_a_line_file = open(self.LINE_BASE_PATH + a_line + 
					"/brightness", 'wb')
		self.hb_b_line_file = open(self.LINE_BASE_PATH + b_line + 
					"/brightness", 'wb')
		self.set_a_line(0)
		self.set_b_line(0)
		self.__tid = thread.start_new_thread(self.__pwm_thread_func, 
							(None, None))
		print("motor has been set up with: " + a_line + ", " + b_line)
		return

motors = []

def client_thread(client_socket, dummy):
	while 1:
		recv = client_socket.recv(1)
		if not recv: break
		#		print("incoming data: 0x" + recv.encode('hex'))
		motor_id = ord(recv)>>4
		motor_speed = 7 - (ord(recv) & 0x0f)
		#print("setting motor " + str(motor_id) + " speed to " + 
		#	str(motor_speed))
		try:
			motors[motor_id].speed = motor_speed;
		except IndexError:
			print("bad motor index!")
	return

def signal_handler(signal, frame):
	print("exiting")
	for motor in motors:
		motor.speed = 0
	server_socket.close()	
	sys.exit()

print("hello!")		


print("setting up motors")
motors.append(Motor("soc:red:internet", "soc:red:power"))
motors.append(Motor("soc:blue:unlabeled", "soc:blue:usb3"))

print("creating socket")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 1337))
server_socket.listen(5)

print("all systems go!")

signal.signal(signal.SIGINT, signal_handler)

client_tids = []

while (1):
	(client_socket, address) = server_socket.accept()
	print("new client connection from " + str(address[0]) + "!")
	client_tids.append(thread.start_new_thread(client_thread, 
			(client_socket, None)))
	
thread.exit()
print("bye!")

