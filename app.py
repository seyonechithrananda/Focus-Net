# app.py
import os, socket, struct, json
import datetime
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from forms import IPForm
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO, send, join_room, leave_room
import _thread, time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
socketio = SocketIO(app)
sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
data= []

##############
## AI MODEL ##
##############

state_dict = torch.load("EEG_Model.pth")
class EEG_Model(nn.Module):
    def __init__(self):
        super(EEG_Model, self).__init__()
        self.fc1 = nn.Linear(3, 15)
        self.fc2 = nn.Linear(15, 15)
        self.fc3 = nn.Linear(15, 1)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        # add layer, with relu activation function
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.sigmoid(self.fc3(x))        
        return x

# initialize the NN
model = EEG_Model()
model = model.double()
model.load_state_dict(torch.load('EEG_Model.pth'))
model.eval()

def getBand():
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        if "gamma_absolute" in str(data):
            break
    title, args, flt1, flt2, flt3, flt4 = struct.unpack('>36s8sffff', data)
    EEG = np.array([flt1, flt3, flt4])
    EEG = torch.from_numpy(EEG)
    focus = int(model(EEG) * 100)
    date = str(datetime.datetime.now())
    print(EEG)
    package = [date, focus]
    socketio.emit("EEG", json.dumps(package), json=True, broadcast=True)
    print('sent message')
    return np.array(EEG)

def streamLoop():
    while True:
        time.sleep(0.5)
        getBand()

try:
    _thread.start_new_thread(streamLoop)

except:
    print('Error! ----')
print('Success')


#########################
##### SQL DATABASE ######
#########################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

#########################
#####    MODELS    ######
#########################

class Puppy(db.Model):

    __tablename__ = 'puppies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    owner = db.relationship('Owner', backref='puppy', uselist=False)


    def __init__(self, name):
        self.name = name

    def __repr__(self):
        if self.owner:
            return "Puppy name is {} and owner is {}".format(self.name, self.owner.name)
        else:
            return "Puppy name is {} and it has no owner yet".format(self.name)

class Owner(db.Model):

    __tablename__ = "owners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    puppy_id = db.Column(db.Integer, db.ForeignKey('puppies.id'))

    def __init__(self, name, puppy_id):
        self.name = name
        self.puppy_id = puppy_id

###########################
##### VIEW FUNCTIONS ######
###########################


@app.route('/', methods=["GET", "POST"])
def index():
    form = IPForm()

    if form.validate_on_submit():
        UDP_IP = form.address.data
        UDP_PORT = form.port.data
        print(UDP_IP, UDP_PORT)
        sock.bind((UDP_IP, UDP_PORT))
        return redirect(url_for('dashboard'))     

    
    return render_template('index.html', form=form)

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    return render_template('dashboard.html', data=data)

@socketio.on('join')
def on_join(data):
    join_room('clients')
    print("User Connected")
    #send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    leave_room('clients')
    print("User Disconnected")

    #send(username + ' has left the room.', room=room)
'''
@app.route('/add', methods=['GET', 'POST'])
def add_pup():

    form = AddForm()

    if form.validate_on_submit():
        name = form.name.data

        new_pup = Puppy(name)
        db.session.add(new_pup)
        db.session.commit()

        return redirect(url_for('list_pup'))

    return render_template('add.html', form=form)

@app.route('/list')
def list_pup():
    puppies = Puppy.query.all()
    return render_template('list.html', puppies=puppies)


@app.route('/delete', methods=['GET', 'POST'])
def del_pup():
    form = DeleteForm()

    if form.validate_on_submit():
        id = form.id.data
        pup = Puppy.query.get(id)
        db.session.delete(pup)
        db.session.commit()

        return redirect(url_for('list_pup'))
    return render_template('delete.html', form=form)


@app.route('/owner', methods=["GET", "POST"])
def add_owner():
    form = OwnerForm()

    if form.validate_on_submit():
        owner = form.owner_name.data
        puppy_id = form.puppy_id.data
        db.session.add(Owner(owner, puppy_id))
        db.session.commit()

        return redirect(url_for('list_pup'))

    return render_template("owner.html", form=form)

'''

if __name__ == '__main__':
    socketio.run(app)
