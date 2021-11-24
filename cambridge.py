import requests
from bs4 import BeautifulSoup
from .basic import html_headers, color_word, blur_color_text
from . import yandex

def add_phrases(word, block, all_phrases):
    cnt = all_phrases['cnt']
    lst_phrases = all_phrases['phrases']
    lst_definitions = []
    phrases = block.find_all('div', class_=['def-body','ddef_b'])
    for phrase in phrases:
        if phrase is None:
            continue
        txt_phrase = phrase.get_text()
        if txt_phrase.lower().find(word) == -1:
            continue
        phrase_trs = yandex.get_data(txt_phrase)
        txt_phrase = color_word(word,txt_phrase)
        txt_phrase = '<b>"'+txt_phrase+'"</b><BR><i>"'+phrase_trs+'"</i>'
        definitions = block.find_all('div', class_=['def','ddef_d','db'])
        for definition in definitions:
            cnt+=1
            txt_definition = definition.get_text()
            definition_trs = yandex.get_data(txt_definition)
            txt_definition = blur_color_text(txt_definition)+'<BR>'+blur_color_text(definition_trs)
            lst_definitions.append(f'{cnt:02}. {txt_definition}')
        lst_phrases.append('<BR>'.join(lst_definitions)+'<BR>'+txt_phrase+'<BR>')
    return {'cnt':cnt, 'phrases':lst_phrases}

def search(word):
    all_phrases = {'cnt':0,'phrases':[]}
    cnt = 0
    with requests.Session() as session:
        source = session.get(f'https://dictionary.cambridge.org/pt/dicionario/ingles/{word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")
        senses = soup.find_all('div', class_=['sense-body','dsense_b'])
        for sense in senses:
            def_blocks = sense.find_all('div', class_=['def-block','ddef_block'])
            for block in def_blocks:
                all_phrases = add_phrases(word, block, all_phrases)
    return ['','','','<BR>'.join(all_phrases['phrases']),'']


#print(search('witless'))