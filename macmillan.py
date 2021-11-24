import requests
from bs4 import BeautifulSoup
from .basic import html_headers, convert_lang, capitalize_first, color_word, insert_end_dot
from . import yandex

def blur_color_text(txt):
    return f'<font color="#c7c7c7"><i>{txt}</i></font>'

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

def blur_explanation_bold_phrase(word,txt):
    dot = txt.find(':')
    if dot > 0:
        explanation = txt[:dot+1]
        phrase = txt[dot+1:]
        phrasetrs = yandex.get_data(phrase)
        phrase = color_word(word,phrase)
        explanation = blur_color_text(explanation)
        phrase = f'<b>"{phrase}"</b>'
        txt = explanation+'<BR>'+phrase+'<BR><i>"'+phrasetrs+'"</i><BR>'
    else:
        phrasetrs = yandex.get_data(txt)
        txt = color_word(word,txt)
        txt = f'<b>"{txt}"</b><BR><i>"{phrasetrs}"</i><BR>'
    return txt

def search(word):
    txt_definitions = []
    txt_examples = []
    txt_ipas = []
    with requests.Session() as session:
        source = session.get(f'https://www.macmillandictionary.com/us/dictionary/american/{word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")
        cntdef=0
        senses = soup.find_all('div', class_='SENSE-CONTENT')
        for sense in senses:
            span_definition = sense.find('span', class_='DEFINITION')

            cntdef+=1
            txt_def = span_definition.text.replace('\n',' ').replace('  ',' ')
            txt_def = capitalize_first(txt_def)
            sections = txt_def.split(':')
            if len(sections) > 1:
                sections[1] = capitalize_first(sections[1])
                txt_def = '<u>'+sections[0]+'</u>: '+sections[1]
            else:
                txt_def = sections[0]
            txt_def = insert_end_dot(txt_def)
            txt_definitions.append(f'{cntdef}. {txt_def}')

            span_prons = sense.find_all('span', class_='PRON')
            for pron in span_prons:
                txt_ipa = pron.text.replace('  ',' ').replace('/','')
                txt_ipas.append(txt_ipa)

            div_examples = sense.find_all('div', class_='EXAMPLES')
            if len(div_examples) > 0:
                deftrs = yandex.get_data(txt_def)
                txt_def = color_word(word,txt_def)
                txt_def = f'{cntdef:02}. '+blur_color_text(txt_def)+'<BR>'+blur_color_text(deftrs)
                if has_colored_word(word,txt_def) == False:
                    txt_examples.append(txt_def)
            for p_example in div_examples:
                text = p_example.text.replace('\n',' ').replace('  ',' ')
                text = capitalize_first(text)
                text = insert_end_dot(text)
                text = blur_explanation_bold_phrase(word,text)
                if has_colored_word(word,text) == False:
                    txt_examples.append(text)

    return ['', '<br>'.join(txt_definitions), ', '.join(txt_ipas), '<br>'.join(txt_examples)]

#print(search('ambition'))