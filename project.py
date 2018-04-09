from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
from consts import PLAYERS
from ibm_utils import startup_discovery
from str_utils import uni2str

app = Flask(__name__, template_folder='templates')
NAME = None
CPU, P1 = 'cpu', 'P1'
turns = P1 
cur_quest = 0
points = [0, 0]

def validate_answer(answer):
    return True, "yes"

def find_answer(question):
    return True, "Your mom"

def gen_question():
    return "What is this?"

def calc_result():
    result = 'CPU wins'
    if points[1] > points[0]:
        result = 'P1 wins'
    elif points[1] == points[0]:
        result = 'Draw'
    score_board = 'Caridin: ' + str(points[0]) + '; ' + NAME + ': ' + str(points[1])
    return result, score_board

@app.route('/', methods=['GET', 'POST'])
def playGame():
    global NAME, points, turns, cur_quest

    if request.method == 'GET':
        NAME, points, turns, cur_quest = None, [0, 0], P1, 0
        return render_template('index.html')
    elif request.method == 'POST':
        data = request.json
        if NAME is None:
            NAME = uni2str(data['reply'])
            bot_reply = 'Hello ' + NAME + '! Let\'s get started! You will ask first.'
            return jsonify(name = NAME, reply = bot_reply)
        elif cur_quest >= 10:
            return jsonify(reply = 'The game is over. Please reload to play again.')
        elif turns == P1:
            turns = CPU
            question = uni2str(data['reply'])
            is_correct, reply = find_answer(question)
            if is_correct:
                points[0] += 1
            else:
                points[1] += 1
            cur_quest += 1
            bot_question = gen_question()
            print bot_question
            return jsonify(reply = reply, question = bot_question)
        elif turns == CPU:
            turns = P1
            answer = uni2str(data['reply'])
            is_correct, reply = validate_answer(answer)
            if is_correct:
                points[1] += 1
            else:
                points[0] += 1
            cur_quest += 1
            if cur_quest == 10:
                result, score_board = calc_result()
                return jsonify(reply = reply, result = result, score_board = score_board)
            else:
                return jsonify(reply = reply)
        else:
            return jsonify(error = 'POST request error')

if __name__ == "__main__":
    startup_discovery()
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
