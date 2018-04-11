from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from players_info import PLAYERS
from ibm_utils import startup_discovery, search, get_entities_type, get_keywords, \
        analyze_article, get_entities_type_nlu
from str_utils import * 

import cf_deployment_tracker
import json
import re
import os
import random

cf_deployment_tracker.track()

app = Flask(__name__, template_folder='templates')
NAME = None
PLAYER_NAMES = None
CPU, P1 = 'cpu', 'P1' # Used to identify turns
turns = P1 
cur_quest = 0
points = [0, 0] # 0: cpu score, 1: player score

# Robot's category of questions
BOT_QT_CATEGORY = ['position', 'player', 'team', 'entities']

# Possible article urls used for entities category questions
ARTICLE_URLS = [
    "http://www.espn.com/espn/print?id=22993116&type=Story&imagesPrint=off",
    "http://www.espn.com/espn/print?id=23055725&type=HeadlineNews&imagesPrint=off",
    "http://www.espn.com/espn/print?id=23020772",
    "http://www.espn.com/espn/print?id=23019054",
    "http://www.espn.com/espn/print?id=23007564&type=Story&imagesPrint=off"
]
POSITIONS = [["G"], ["G", "F"], ["C"]]
bot_qt_category = '' # Current bot question category
bot_qt_expected_ans = '' # Current bot question expected answer
question_history = [] # Storing bot previous questions

# Check if bot ask the same question
def check_repeated_question(question):
    global question_history
    return question in question_history

# Generate chat bot questions
# Return question category (in str), question, and expected answer (or possible answers)
def gen_question():
    global question_history
    is_repeated_history = True
    while is_repeated_history:
        # Pick random question category: position, player, entities
        question_category = random.choice(BOT_QT_CATEGORY)
        if question_category == 'position':
            player = random.choice(PLAYERS.keys())
            question = "What is the position of " + player + "? (Guard/Forward/Center)"
            position = get_position_str(PLAYERS[player]['role']) 
            is_repeated_history = check_repeated_question(question)
            if is_repeated_history:
                continue
            else:
                return question_category, question, position
        elif question_category == 'team':
            player = random.choice(PLAYERS.keys())
            question = "Which team does " + player + " in?"
            is_repeated_history = check_repeated_question(question)
            if is_repeated_history:
                continue
            else:
                return question_category, question, PLAYERS[player]['team']
        elif question_category == 'player':
            player = random.choice(PLAYERS.keys())
            team = PLAYERS[player]['team']
            position = PLAYERS[player]['role']
            question = "Whose position is " + get_position_str(position) + \
                    " in " + team + '?'
            expected_ans = {
                'position': position,
                'team': team,
            }
            is_repeated_history = check_repeated_question(question)
            if is_repeated_history:
                continue
            else:
                return question_category, question, expected_ans 
        elif question_category == 'entities': 
            article_url = random.choice(ARTICLE_URLS)
            analysis = analyze_article(article_url)
            entities = analysis['entities']
            entity = random.choice(entities)
            entity_txt = uni2str(entity['text'])
            expected_type = split_cammel(uni2str(entity['type']))
            entity_types = get_entities_type_nlu(entities)
            question = ''
            if len(entity_types) > 1:
                question = 'What is ' + entity_txt + '? (' + ', '.join(entity_types) + ')'
            else:
                question = 'What is ' + entity_txt + '?'
            is_repeated_history = check_repeated_question(question)
            if is_repeated_history:
                continue
            else:
                return question_category, question, expected_type 

# Validate user answer
# Return check if answer is correct (True: correct, False: incorrect, and reply message
def validate_answer(answer):
    global bot_qt_category, bot_qt_expected_ans
    if answer == 'sorry':
        return False, 'no'
    elif bot_qt_category in ['position', 'entities']:
        if bot_qt_expected_ans.lower() != answer.lower():
            return False, 'no'
        else:
            return True, 'yes'
    elif bot_qt_category == 'team':
        # Split team name: '<location> <mascot>' to ['<location>', 'mascot']
        team_names = bot_qt_expected_ans.split(' ') 
        if answer == bot_qt_expected_ans or answer in team_names:
            return True, 'yes'
        else:
            return False, 'no'
    elif bot_qt_category == 'player':
        if (answer not in PLAYERS) or \
                (PLAYERS[answer]['team'] != bot_qt_expected_ans['team']) or \
                (PLAYERS[answer]['role'] != bot_qt_expected_ans['position']):
            return False, 'no'
        else:
            return True, 'yes'

# Find answer based on user question
# Return if bot is correct (True: correct, False: not found) and reply message
def find_answer(question):
    global PLAYER_NAMES

    qt = question
    qt_category, query = '', ''
    question_type, qt = get_question(qt)

    # Invalid question type
    if question_type.lower() not in QUESTIONS:
        return True, "Invalid Question type: +1 for oppononent (which is me btw)"
    
    # Extract quoted phrase from question
    qt, phrases = extract_quote_str(qt)

    # Extract names from question
    qt, names = extract_name(qt)

    # Create querry string
    for phrase in phrases:
        query += '\'' + phrase + '\' '
    for name in names:
        query += '\'' + name + '\' '
    query += qt

    search_result = search(query)

    # If there is not result than bot is wrong
    if search_result['matching_results'] == 0:
        return False, "I don't know"
    search_result = search_result['results']

    # Question is about a position of a player
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
    elif ('player' in qt) and (question_type == 'which'): # Question is about a player
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
    elif ('team' in qt) and (question_type == 'which'): # Question is about team
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
    elif (len(phrases) > 0) and (len(names) > 0): # Question is about skill
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
    elif (len(names) == 1): # Question is about an entity
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


# Calculate result after the game
# Return string display of result and string scoreboard
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
    global NAME, points, turns, cur_quest, bot_qt_category, bot_qt_expected_ans

    if request.method == 'GET':
        NAME, points, turns, cur_quest = None, [0, 0], P1, 0
        return render_template('index.html')
    elif request.method == 'POST':
        data = request.json
        if NAME is None: # Initially, ask use for name
            NAME = uni2str(data['reply'])
            bot_reply = 'Hello ' + NAME + '! Let\'s get started! You will ask first.'
            return jsonify(name = NAME, reply = bot_reply)
        elif cur_quest >= 10: # if number of questions is 10 or over. Don't continue playing
            return jsonify(reply = 'The game is over. Please reload to play again.')
        elif turns == P1: # If this is player turns to ask question
            turns = CPU
            question = uni2str(data['reply'])
            is_correct, reply = find_answer(question)
            if is_correct:
                points[0] += 1
            else:
                points[1] += 1
            cur_quest += 1
            bot_qt_category, bot_question, bot_qt_expected_ans = gen_question()
            return jsonify(reply = reply, question = bot_question)
        elif turns == CPU: # If this is CPU turns to ask question
            turns = P1
            answer = uni2str(data['reply'])
            is_correct, reply = validate_answer(answer)
            if is_correct:
                points[1] += 1
            else:
                points[0] += 1
            cur_quest += 1
            if cur_quest == 10: # Check if this is the last question
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
