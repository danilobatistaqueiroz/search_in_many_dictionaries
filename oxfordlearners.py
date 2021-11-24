import requests
from bs4 import BeautifulSoup
from .basic import html_headers, blur_color_text, color_word
from . import yandex

def search(word):
    all_synonyms = []
    all_definitions = []
    all_phrases = []
    with requests.Session() as session:
        source = session.get(f'https://www.oxfordlearnersdictionaries.com/us/search/english/direct/?q={word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")
        content = soup.find('div', id="entryContent")
        if content is None:
            return ['','','','','']
        senses_ol = content.find('ol', class_="senses_multiple")
        if senses_ol is None:
            senses_ol = content.find('ol', class_="sense_single")
        senses = senses_ol.find_all('li', class_="sense")
        cnt_phr=0
        cnt_def=0
        for sense in senses:
            cnt_def+=1
            definition = sense.find('span', class_='def').get_text()
            all_definitions.append(f'{cnt_def:02}. '+definition)
            xrefs = sense.find('span', class_='xrefs')
            txt_prefix = ''
            if xrefs is not None:
                prefix = xrefs.find('span',class_='prefix')
                if prefix is not None:
                    txt_prefix = prefix.get_text()
            txtsyn = ''
            if txt_prefix.upper() == 'SYNONYM':
                synonyms = xrefs.find_all('a')
                lst_synonyms = []
                for synonym in synonyms:
                    lst_synonyms.append(synonym.get_text())
                    all_synonyms.append(synonym.get_text())
                txtsyn = 'synonyms:'+','.join(lst_synonyms)
            examples = sense.find('ul', class_='examples')
            structure = ''
            phrase = ''
            phrases = []
            if examples is not None:
                items = examples.find_all('li')
                for item in items:
                    cf = item.find('span', class_='cf')
                    if cf is not None:
                        structure = cf.get_text()+'<BR>'
                    x = item.find('span', class_='x')
                    if x is not None:
                        phrase = x.get_text()
                        if phrase.find(word) == -1:
                            continue
                        if len(phrase) > 75:
                            continue
                        phrasetrs = yandex.get_data(phrase)
                        phrase = color_word(word,phrase)
                    phrases.append('<B>"'+phrase+'"</B><BR><i>"'+phrasetrs+'"</i><BR><BR>')
            if len(phrases) > 0:
                syn = ''
                if txtsyn != '':
                    syn = blur_color_text(txtsyn)+'<BR>'
                deftrs = ''
                deftxt = ''
                if definition != '':
                    deftxt = blur_color_text(definition)+'<BR>'
                    definitiontrs = yandex.get_data(definition)
                    if definitiontrs != '':
                        deftrs = blur_color_text(definitiontrs)+'<BR>'
                cnt_phr+=1
                all_phrases.append(f'{cnt_phr:02}. '+
                deftxt+
                deftrs+
                syn+
                ''.join(phrases))
        txt_phrases = '<BR>'.join(all_phrases)
        if txt_phrases.endswith('<BR><BR>'):
            txt_phrases = txt_phrases[:-8]
    return ['','<BR>'.join(all_definitions),'',txt_phrases,'','','',','.join(all_synonyms)]


#print(search('bat'))