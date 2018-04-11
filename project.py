from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from consts import PLAYERS
from ibm_utils import startup_discovery, search, get_entities_type, get_keywords
from str_utils import * 

# import cf_deployment_tracker
import json
import re
import os

# cf_deployment_tracker.track()

app = Flask(__name__, template_folder='templates')
NAME = None
PLAYER_NAMES = None
CPU, P1 = 'cpu', 'P1'
turns = P1 
cur_quest = 0
points = [0, 0]

def validate_answer(answer):
    return True, "yes"

def find_answer(question):
    global PLAYER_NAMES
    qt = question
    qt_category, query = '', ''
    question_type, qt = get_question(qt)
    if question_type.lower() not in QUESTIONS:
        return True, "Invalid Question type: +1 for oppononent (which is me btw)"
    qt, phrases = extract_quote_str(qt)
    qt, names = extract_name(qt)
    for phrase in phrases:
        query += '\'' + phrase + '\' '
    for name in names:
        query += '\'' + name + '\' '
    query += qt

    search_result = search(query)

    if search_result['matching_results'] == 0:
        return False, "I don't know"
    search_result = search_result['results']

    if ('position' in qt) and (len(names) == 1):
        for doc in search_result:
            text = doc['text']
            index_list = [i.start() for i in re.finditer(names[0], text)]
            role = ''
            for index in index_list:
                if role != '':
                    break
                sentence = uni2str(get_sentence_by_index(text, index).lower())
                if (names[0].lower() in sentence):
                    role = ''
                    if 'forward' in sentence:
                        role += 'Forward'
                    if 'guard' in sentence:
                        if role != '':
                            role += '/'
                        role += 'Guard'
                    if 'center' in sentence:
                        role = 'Center'
                    if role != '':
                        return True, role
            if role == '':
                return False, "I don't know"
    elif ('player' in qt) and (question_type == 'which'):
        if PLAYER_NAMES is None:
            PLAYER_NAMES = []
            for key, val in PLAYERS.iteritems():
                PLAYER_NAMES.append(key.lower())
        is_found_name = False
        for doc in search_result:
            if is_found_name:
                break
            text = doc['text']
            is_found_name = False
            if len(phrases) > 0:
                for phrase in phrases:
                    index_list = [i.start() for i in re.finditer(phrase.lower(), text.lower())]
                    for index in index_list:
                        sentence = uni2str(get_sentence_by_index(text, index))
                        sentence, sentence_names = extract_name(sentence)
                        for sentence_name in sentence_names:
                            if sentence_name.lower() in PLAYER_NAMES:
                                is_found_name = True 
                                return True, sentence_name
            elif len(names) > 0: 
                for name in names:
                    index_list = [i.start() for i in re.finditer(name.lower(), text.lower())]
                    for index in index_list:
                        sentence = uni2str(get_sentence_by_index(text, index))
                        sentence, sentence_names = extract_name(sentence)
                        for sentence_name in sentence_names:
                            if (sentence_name.lower() in PLAYER_NAMES) and (sentence_name.lower() != name.lower()):
                                is_found_name = True 
                                return True, sentence_name
            else:
                qt_words = qt.split(' ')
                for qt_word in qt_words:
                    if qt_word == '':
                        continue
                    index_list = [i.start() for i in re.finditer(qt_word.lower(), text.lower())]
                    for index in index_list:
                        sentence = uni2str(get_sentence_by_index(text, index))
                        sentence, sentence_names = extract_name(sentence)
                        for sentence_name in sentence_names:
                            if (sentence_name.lower() in PLAYER_NAMES):
                                is_found_name = True 
                                return True, sentence_name
            if not is_found_name:
                return False, "I don't know"
    elif ('team' in qt) and (question_type == 'which'):
        for doc in search_result:
            text = doc['text']
            is_found_team = False
            if len(names) > 0:
                index_list = [i.start() for i in re.finditer(names[0].lower(), text.lower())]
                for index in index_list:
                    sentence = uni2str(get_sentence_by_index(text, index))
                    is_right_sentence = True
                    for name in names:
                        if name not in sentence:
                            is_right_sentence = False
                            break
                    if not is_right_sentence:
                        continue
                    sentence, sentence_names = extract_name(sentence)
                    for sentence_name in sentence_names:
                        entities_types = get_entities_type(doc, sentence_name)
                        print sentence_name
                        print entities_types
                        if (sentence_name not in names) and ("Organization" in entities_types):
                            is_found_team = True
                            return True, sentence_name
            elif len(phrases) > 0:
                for phrase in phrases:
                    index_list = [i.start() for i in re.finditer(phrase.lower(), text.lower())]
                    for index in index_list:
                        sentence = uni2str(get_sentence_by_index(text, index))
                        sentence, sentence_names = extract_name(sentence)
                        for sentence_name in sentence_names:
                            entities_types = get_entities_type(doc, sentence_name)
                            if "Organization" in entities_types:
                                is_found_name = True 
                                return True, sentence_name
            if not is_found_team:
                return False, "I don't know"
    elif (len(phrases) > 0) and (len(names) > 0):
        is_found_skill = False
        for doc in search_result:
            text = doc['text']
            for phrase in phrases:
                index_list = [i.start() for i in re.finditer(phrase.lower(), text.lower())]
                for index in index_list:
                    sentence = uni2str(get_sentence_by_index(text, index))
                    keywords = get_keywords(doc)
                    for keyword in keywords:
                        if keyword[0] >= 'A' and keyword[0] <= 'Z':
                            continue
                        elif keyword in sentence:
                            is_found_skill = True
                            return True, keyword
        if not is_found_skill:
            return False, "I don't know"
    elif (len(names) == 1):
        is_found_entity = False
        for doc in search_result:
            for name in names:
                entities_types = get_entities_type(doc, name)
                if entities_types != []:
                    is_found_entity = True
                    return True, ', '.join(entities_types)
        if not is_found_entity:
            return False, "I don't know"
    else:
        return False, "I don't know"

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

port = int(os.getenv('PORT', 8000))

if __name__ == "__main__":
    startup_discovery()
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = port)
