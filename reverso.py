import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString
import json
import re
from .basic import html_headers, capitalize_first, insert_end_dot

headers_post = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST,OPTIONS',
    'Access-Control-Allow-Headers': '*',
    'Access-Control--Max-Age': '86400',
    'Content-Type': 'application/json',
    'Accept': 'text/plain',
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
}

languagues = {'ingles':'english','portugues':'portuguese','espanol':'spanish','frances':'french','alemao':'germani'}

def convert_lang(language):
    if language in languagues:
        return languagues[language]
    else:
        return language

def color_word(txt):
    txt = re.sub(r'<em class="both">(.*)</em>', '<font color="#ff0000">\g<1></font>', txt)
    txt = re.sub(r'<em>(.*)</em>','<font color="#ff0000">\g<1></font>',txt)
    return txt

def dic_translations_to_text(lst_dic):
    txt = ''
    if len(lst_dic) == 0:
        return ''
    for dic in lst_dic:
        txt+=f'({dic["freq"]}){dic["text"]},'
    return txt[:-1]

def phrases(word,term,abrv_target,lang_target):
    data = {"source_text":word,"target_text":term,"source_lang":"en","target_lang":abrv_target,"npage":1,"mode":0}
    source = requests.post(f'https://context.reverso.net/translation/english-{lang_target}/{word}', json=data, headers=headers_post)
    r_json = source.json()
    phrases=[]
    if len(r_json) > 0:
        phrases.append({'phrase':color_word(r_json['list'][0]['s_text']), 'translation':color_word(r_json['list'][0]['t_text'])})
    #if len(r_json) > 1:
    #    phrases.append({'phrase':color_word(r_json['list'][1]['s_text']), 'translation':color_word(r_json['list'][1]['t_text'])})
    #if len(r_json) > 2:
    #    phrases.append({'phrase':color_word(r_json['list'][2]['s_text']), 'translation':color_word(r_json['list'][2]['t_text'])})
    #if len(r_json) > 3:
    #    phrases.append({'phrase':color_word(r_json['list'][3]['s_text']), 'translation':color_word(r_json['list'][3]['t_text'])})
    #if len(r_json) > 4:
    #    phrases.append({'phrase':color_word(r_json['list'][4]['s_text']), 'translation':color_word(r_json['list'][4]['t_text'])})
    #if len(r_json) > 5:
    #    phrases.append({'phrase':color_word(r_json['list'][5]['s_text']), 'translation':color_word(r_json['list'][5]['t_text'])})
    return phrases

def remove_last_br(text):
    if len(text) > 4:
        text = text[:-4]
    return text

def phrases_text(items):
    text = ''
    cnt = 0
    for item in items:
        cnt+=1
        #text+=f'.{cnt}.<br>'
        for phrase in item:
            text+='<b>"'+phrase['phrase']+'"</b><br>'
            text+='<i>"'+phrase['translation']+'"</i><br><br>'
    text = remove_last_br(text)
    return text

def phrases_tr_text(items):
    text = ''
    cnt = 0
    for item in items:
        cnt+=1
        #text+=f'.{cnt}.<br>'
        for phrase in item:
            text+=phrase['translation']+'<br>'
    return text

def search(word,abrv_target,lang_target):
    lang_target = convert_lang(lang_target)
    lst_translations = []
    with requests.Session() as session:
        source = session.get(f'https://context.reverso.net/translation/english-{lang_target}/{word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")
        cnt=0
        freq=0
        text=''
        div_translations = soup.find('div', attrs={"id" : "translations-content"})
        for translation in div_translations.children:
            cnt+=1
            if type(translation) == NavigableString:
                continue
            text = translation.get_text()
            freq = ''
            if 'data-freq' in translation:
                freq = int(translation['data-freq'])
            text = text.replace('\n','').strip()
            if text.lower() == word or len(text) == 0:
                continue
            lst_translations.append({'freq':freq,'text':text})
    sorted_words = lst_translations #sorted(lst_translations, key=lambda row: (row['freq']), reverse=True)
    txt_translations = dic_translations_to_text(sorted_words)
    cnt = 0
    items = []
    for term in sorted_words:
        cnt+=1
        items.append(phrases(word,term['text'],abrv_target,lang_target))
        if cnt == 6:
            break
    txt_phrases_en = phrases_text(items)
    #txt_phrases_tr = phrases_tr_text(items)

    #txt_phrases = '<b>"'+txt_phrases_en+'"</b><br><i>"'+txt_phrases_tr+'"</i><br>'
    return [txt_translations,'','',txt_phrases_en]

#print(search('weed','pt','portuguese'))
#print(phrases('whacked','matar'))