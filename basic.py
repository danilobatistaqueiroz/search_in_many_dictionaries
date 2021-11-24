html_headers = {
   'Content-Type': 'application/xhtml+xml',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST,OPTIONS',
    'Access-Control-Allow-Headers': '*',
    'Access-Control--Max-Age': '86400',
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
}

languagues = {'english':'ingles','portuguese':'portugues','spanish':'espanol','french':'frances','germani':'alemao'}

def convert_lang(language):
    if language in languagues:
        return languagues[language]
    else:
        return language

def has_color(txt):
    return txt.find('<font color="#ff0000">') > -1

def has_colored_word(word,txt):
    match = f'<font color="#ff0000">{word}</font>'
    match1 = f'{match} '
    match2 = f'{match},'
    match3 = f'{match}!'
    match4 = f'{match}?'
    match5 = f'{match}.'
    match6 = f'{match};'
    match7 = f'{match}:'
    matches = [match1,match2,match3,match4,match5,match6,match7]
    has = False
    for m in matches:
        if txt.find(m) > -1:
            has = True
    return has

def is_word_in_end(position, ini, word, txt):
    '''is the word or one of the flexions in the end of phrase?'''
    return position == -1 and ini+len(word)+4 >= len(txt)

def verify_end_word(txt,ini):
    '''verify the end of a word'''
    position = -1
    for item in ['.',',',';',':',' ','!','?','"',"'"]:
        pos = txt.find(item,ini)
        if pos > -1:
            if position != -1 and pos < position:
                position = pos+1
            elif position == -1:
                position = pos+1
    return position

def color_word(word,txt):
    ini = txt.lower().find(word.lower())
    if ini > -1:
        position = verify_end_word(txt,ini)
        if is_word_in_end(position, ini, word, txt):
            position = len(txt)+1
    if ini > -1 and position > -1:
        before = txt[:ini]
        after = txt[position-1:]
        colored = txt[ini:position-1]
        newtxt = before+'<font color="#ff0000">'+colored+'</font>'+after
    else:
        newtxt = txt.replace(word,f'<font color="#ff0000">{word}</font>')
        newtxt = newtxt.replace(word.capitalize(),f'<font color="#ff0000">{word.capitalize()}</font>')
    return newtxt

def blur_color_text(txt):
    return f'<font color="#c7c7c7"><i>{txt}</i></font>'

def emphasie_text(txt):
    return f'<i><u><font color="#aa4444">{txt}</font></u></i>'

def capitalize_first(txt):
    """capitalize the first letter"""
    if txt is not None and len(txt)>1:
        return txt[0:1].upper()+txt[1:]
    else:
        return txt

def insert_end_dot(text):
    text = text.strip()
    if text[-1:] != '.':
        text = text.strip()+'.'
    return text

def insert_quotations(text):
    text = text.strip()
    if text.startswith('"') or text.startswith("'") or text.startswith("´") or text.startswith("`"):
        return text
    else:
        return '"'+text+'"'

#print(color_word('warp',"The young criminal\'s unhappy childhood had warped his outlook on life."))