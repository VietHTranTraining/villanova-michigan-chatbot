import unicodedata

QUESTIONS = ['which', 'what'] # Types of questions
QUOTES = ['\'', '"'] # Quoute characters
SPEC_CHARS = [',', '.', '?', '!'] # Special characters
END_SENTENCE = ['.', '!', '?', '\n'] # Sentence-ending characters
BLANK_SPACES = [' ', '\n', '\t'] # Blank spaces

# Find sentence in the paragraph where the index is located
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

# Insert space between each word in cammel case string 
# Return the updated string 
def split_cammel(cammel_str):
    res = ''
    for i in range(len(cammel_str)):
        c = cammel_str[i]
        if c >= 'A' and c <= 'Z' and i != 0:
            res += ' '
        res += c
    return res

# Exctract phrase enclosed in quotes or double quotes
# Return the sentence and the list of quoted phrases
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
# Return the type of question (in str) and the remaining sentence without the WH question
def get_question(sentence):
    first_word = get_first_word(sentence)
    res_sentence = sentence.replace(first_word, '', 1)
    first_word = first_word.lower()
    if first_word in QUESTIONS:
        return first_word, res_sentence 
    return 'NO', sentence

# Cut the name from the sentence
# Return the remaining sentence and list of name (in that order)
def extract_name(sentence):
    res_name, res, name_holder = [], [], []
    word_list = sentence.split(' ')
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

# Convert list of positions initial to string literal
def get_position_str(pos_lst):
    res = ''
    if "G" in pos_lst:
        res += "Guard"
    if "F" in pos_lst:
        if res != '':
            res += '/'
        res += "Forward"
    if "C" in pos_lst:
        res += "Center"
    return res


