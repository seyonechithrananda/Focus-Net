import socket
import struct

print('Program Initiated')

UDP_IP = "10.33.133.249"
UDP_PORT = 7000

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

print("socket binded")

while True:
    print("looping")
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print(data)
