from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
from consts import PLAYERS
from ibm_utils import startup_discovery
from str_utils import uniToStr

app = Flask(__name__, template_folder='templates')
NAME = None

@app.route('/', methods=['GET', 'POST'])
def playGame():
    global NAME
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        data = request.json
        if NAME is None:
            NAME = uniToStr(data['reply'])
            bot_reply = 'Hello ' + NAME + '! Let\'s get started'
            return jsonify(name = NAME, reply = bot_reply)
        else:
            return jsonify(reply = 'gg')

if __name__ == "__main__":
    startup_discovery()
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
