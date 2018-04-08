from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
from consts import PLAYERS
from ibm_utils import startup_discovery

app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def searchTeams():
    return render_template('index.html')

if __name__ == "__main__":
    startup_discovery()
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
