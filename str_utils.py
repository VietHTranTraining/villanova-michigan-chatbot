import unicodedata

QUESTIONS = ['which', 'what']
QT_CATEGORY = ['position', 'player', 'team', 'skill', '']
UNIMPORT_WORDS = ['was', 'were', 'in', 'on', '']
QUOTES = ['\'', '"']
SPEC_CHARS = [',', '.', '?', '!']
END_SENTENCE = ['.', '!', '?', '\n']
BLANK_SPACES = [' ', '\n', '\t']

def is_number(char):
    return char >= '1' and char <= '9'

# Find sentence in the string where the index is located
def get_sentence_by_index(paragraph, index):
    left, right = index, index
    while (left >= 0) and (paragraph[left] not in END_SENTENCE):
        left -= 1
    left += 1
    while (right < len(paragraph)) and \
        ((paragraph[right] not in END_SENTENCE) or \
                ((right < (len(paragraph) + 1)) and (paragraph[right + 1] not in BLANK_SPACES))):
        right += 1
    return paragraph[left:right]

# Convert unicode to string
def uni2str(uncd):
   return unicodedata.normalize('NFKD', uncd).encode('ascii','ignore')

# Insert space between each word in cammel case form
def split_cammel(sentence):
    res = ''
    for i in range(len(sentence)):
        c = sentence[i]
        if c >= 'A' and c <= 'Z' and i != 0:
            res += ' '
        res += c
    return res

# Exctract phrase enclosed in quotes or double quotes
def extract_quote_str(sentence):
    res, quote_holder = '', ''
    res_quote, is_in_quote = [], ' '
    for i in sentence:
        if i in QUOTES:
            if is_in_quote not in QUOTES:
                is_in_quote = i
            elif i == is_in_quote:
                res_quote.append(quote_holder)
                quote_holder = ''
                is_in_quote = ' '
        else:
            if is_in_quote in QUOTES:
                quote_holder += i
            else:
                res += i
    return res, res_quote

# Get first word in a sentence
def get_first_word(sentence):
    res = ''
    for i in sentence:
        if i in [' ', '\t', '\n']:
            return res
        res += i
    return res

# Get first letter of WH questions (What and Which in this case)
def get_question(sentence):
    first_word = get_first_word(sentence)
    res_sentence = sentence.replace(first_word, '', 1)
    first_word = first_word.lower()
    if first_word in QUESTIONS:
        return first_word, res_sentence 
    return 'NO', sentence

# Use this after get_question
def extract_name(sequence):
    res_name, res, name_holder = [], [], []
    word_list = sequence.split(' ')
    for i in word_list:
        if i == '':
            continue
        if i[0] >= 'A' and i[0] <= 'Z':
            if i[-1] in SPEC_CHARS:
                name_holder.append(i[:-1:])
                res_name.append(' '.join(name_holder))
                name_holder = []
            else:
                name_holder.append(i)
        else:
            if name_holder != []:
                res_name.append(' '.join(name_holder))
                name_holder = []
            res.append(i)
    if len(name_holder) > 0:
        res_name.append(' '.join(name_holder))
    return ' '.join(res), res_name
