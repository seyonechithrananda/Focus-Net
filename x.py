from threading import Timer
from flask import Flask

app = Flask(__name__)
DATA = "data"

def update_data(interval):
    Timer(interval, update_data, [interval]).start()
    global DATA
    DATA = DATA + " updating..."

# update data every second
update_data(1)

@app.route("/")
def index():
    return DATA

if __name__ == "__main__":
    app.run(debug=True)