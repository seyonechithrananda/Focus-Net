import socket
import struct

print('Program Initiated')

UDP_IP = "10.33.133.249"
UDP_PORT = 7000

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    if 'gamma_absolute' in str(data):
        print(data)
        title,args,flt1,flt2,flt3,flt4 = struct.unpack('>36s8sffff', data)
        print(flt1, flt2, flt3, flt4)
        print('----------------------------------')