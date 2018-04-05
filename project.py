from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
from consts import PLAYERS

app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def searchTeams():
    return 'gg'

if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
