
import numpy as np
from keras.models import load_model
import socket
import struct
import pygame as pg

model = load_model("models/GAI-sig-500-0.0001.hdf5")


def getBand(band):
  data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
  if band in str(data):
    EEG = struct.unpack('>36s8sffff', data)
    #print(EEG[-3:-1])
    return np.array(EEG[-3:-1])


UDP_IP = "10.33.133.249"
UDP_PORT = 7000
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))


def get_focus():
    average = np.array([0, 0], dtype='float64')
    for i in range(25):        
        eegData = getBand("gamma_absolute")
        if eegData is not None:
            #print(eegData)
            average += eegData
    average /= 5
    average = np.array([average])

    prediction = model.predict(average)
    prediction = [prediction[0][0]*100, prediction[0][1]*100]
    
    prediction[0] = round(prediction[0])
    prediction[1] = round(prediction[1])
    
    final = ''
    '''
    if abs(prediction[0] - prediction[1]) <= 10:
        final = 'Neutral'
    elif prediction[0] > prediction[1]:
        final = 'Concentrated'
    else:
        final = 'Relaxed'
    '''
    if prediction[0] >= 50:
        final="Concentrated"
    else:
        final="Relaxed"
    
    # print("C: ", str(prediction[0])+"%" , "R", str(prediction[1])+"%", average, final)
    # print(int(prediction[0]))
    return int(prediction[0]), int(prediction[1])


pg.init()
screen = pg.display.set_mode((1000, 200))
clock = pg.time.Clock()
running = True
pointsF = [[0, 0], [100, 0], [200, 0], [300, 0], [400, 0], [500, 0], [600, 0], [700, 0], [800, 0], [900, 0], [1000, 0]]
pointsR = [[0, 0], [100, 0], [200, 0], [300, 0], [400, 0], [500, 0], [600, 0], [700, 0], [800, 0], [900, 0], [1000, 0]]

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            Running = False

    pointsF.pop(0)
    for sets in pointsF:
        sets[0] -= 100

    pointsR.pop(0)
    for setsx in pointsR:
        setsx[0] -= 100

    focus, relax = get_focus()
    pointsF.append([1000, 200 - focus * 2])
    pointsR.append([1000, 200 - relax * 2])

    screen.fill((0, 0, 0))
    pg.draw.rect(screen, (0, 0, 255), (0, 500 - focus, 200, focus))
    pg.draw.lines(screen, (0, 0, 255), False, pointsF,  5)
    pg.draw.lines(screen, (255, 0, 0), False, pointsR,  5)
    print(pointsF)
    pg.display.update()
    clock.tick(100)
