import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import string 
from . import yandex
from .basic import html_headers, convert_lang, has_color, capitalize_first, has_colored_word, color_word, insert_end_dot, blur_color_text, emphasie_text, insert_quotations

def search_in_list(list, item):
    for i in range(len(list)):
        if list[i] == item:
            return True
    return False

def is_identification(txt):
    identifications = ['adjective','usually','verb','noun','etc','1.','2.','3.','4.','5.','6.']
    if txt is not None:
        txt=txt.strip().lower()
        return txt in identifications
    return False

def remove_identifications(lst):
    new_lst = []
    for item in lst:
        item = item.replace(' adjective ','')
        item = item.replace(' usually ','')
        item = item.replace(' verb ','')
        item = item.replace(' noun ','')
        item = item.replace(' etc ','')
        item = item.replace(' 1. ','.')
        item = item.replace(' 2. ','.')
        item = item.replace(' 3. ','.')
        item = item.replace(' 4. ','.')
        item = item.replace(' 5. ','.')
        item = item.replace(' 6. ','.')
        item = item.replace('>adjective<','><')
        item = item.replace('>usually<','><')
        item = item.replace('>verb<','><')
        item = item.replace('>noun<','><')
        item = item.replace('>etc<','><')
        item = item.replace('>1.<','>.<')
        item = item.replace('>2.<','>.<')
        item = item.replace('>3.<','>.<')
        item = item.replace('>4.<','>.<')
        item = item.replace('>5.<','>.<')
        item = item.replace('>6.<','>.<')
        item = item.replace("'","")
        new_lst.append(item)
    return new_lst

def generate_index(lst):
    cnt=0
    lsttmp = []
    for item in lst:
        cnt+=1
        lsttmp.append(f'{cnt:02}. {item}')
    return lsttmp

def generate_phrases_index(lst):
    cnt=0
    lsttmp = []
    a_definition = ''
    a_phrase = ''
    lst = sorted(lst, key=lambda row: (row['definition']))
    for item in lst:
        if item['definition'] == a_definition:
            if item['phrase'] != a_phrase:
                lsttmp.append(item['phrase'])
        else:
            cnt+=1
            lsttmp.append(f'{cnt:02}. '+blur_color_text(item['definition'])+'<br>'+item['phrase'])
            a_definition = item['definition']
            a_phrase = item['phrase']
    return lsttmp

def remove_end_ponctuations(txt):
    txt = txt.replace('!;.','!')
    txt = txt.replace('?;.','?')
    txt = txt.replace('?.','?')
    txt = txt.replace(';.','.')
    txt = txt.replace(':.','.')
    txt = txt.replace('!.','!')
    txt = txt.replace('..','.')
    txt = txt.replace(',.','.')
    return txt

def remove_dust(txt):
    txt = txt.replace('()','').replace('→','').replace(' = ','').replace('  ',' ')
    txt = txt.replace('[]','').replace(';;','').replace('()','')
    txt = txt.replace('( )','').replace(';   ;','').replace('  ',' ')
    txt = txt.replace('(= )','').replace('( = )','').replace('(=)','')
    txt = txt.replace('→','').replace('  ;   ','').replace('  ;  ','')
    txt = txt.replace('[+ ]','').replace('[+]','')
    txt = txt.replace(' ; ','').replace('[ ]','')
    txt = remove_first_last_chars(txt)
    return txt

def remove_first_last_chars(txt):
    if len(txt) > 5:
        if ';,.[=: '.find(txt[0:1]) > -1:
            txt = txt[1:]
        if ';,.[=: '.find(txt[-1]) > -1:
            txt = txt[0:-1]
    return txt

def without_good_definition(definition):
    if definition is None:
        return True
    definition = definition.replace(' ','')
    if len(definition) < 5:
        return True
    if contains_special_chars(definition) > 2:
        if len(definition) < 8:
            return True

def contains_special_chars(txt):
    cnt = 0
    invalidcharacters= set(string.punctuation)
    if any(char in invalidcharacters for char in txt):
        cnt+=1
    return cnt

def remove_ini_number(txt):
    for i in range(1,15):
        txt = txt.replace(str(i)+'. ','')
    return txt

def remove_ini_letter(txt):
    for i in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q']:
        if txt.strip().startswith(str(i)+'. '):
            txt = txt.replace(str(i)+'. ','')
    return txt

def remove_lengthy_definition(definitions):
    news = []
    for definition in definitions:
        if len(definition) <= 60:
            news.append(definition)
    return news

class House:
    def select(self,r_house,word):
        if r_house is not None:
            return self.get_pronun(r_house)
        return ''

    def get_pronun(self,r_house):
        pron = r_house.find('span', attrs={"class" : "pron"})
        if pron is not None:
            return pron.get_text().strip()
        else:
            return ''

def definition_in_dictionary(dic_section, lst_definitions):
    if dic_section is not None:
        results = dic_section.find_all('div', 'ds-list')
        for result in results:
            definition = result.get_text().split(':')[0]
            definition = definition.strip()
            if definition.startswith('1.') or definition.startswith('2.') or definition.startswith('3.'):
                definition = remove_ini_number(definition)
                definition = remove_ini_letter(definition)
                definition = insert_end_dot(definition)
                definition = capitalize_first(definition)
                lst_definitions.append(definition)

def join_all_definitions(definitions_hc, definitions_hm, definitions_house):
    definitions_hc = remove_lengthy_definition(definitions_hc)
    definitions_hm = remove_lengthy_definition(definitions_hm)
    definitions_house = remove_lengthy_definition(definitions_house)
    definitions_hc = generate_index(definitions_hc)
    definitions_hm = generate_index(definitions_hm)
    definitions_house = generate_index(definitions_house)
    all_definitions = []
    if len(definitions_hc) > 0:
        all_definitions.append(' ')
        all_definitions.extend(definitions_hc)
    if len(definitions_hm) > 0:
        all_definitions.append(' ')
        all_definitions.extend(definitions_hm)
    if len(definitions_house) > 0:
        all_definitions.append(' ')
        all_definitions.extend(definitions_house)
    return all_definitions

def get_phrases_from_dic(word,dictionaries,uniq_phrases,lst_phrases):
    results = dictionaries.find_all('span', class_='illustration')
    for result in results:
        contents = result.parent.get_text().split(':')
        definition = contents[0]
        phrase = ''
        if len(contents) > 1:
            phrase = contents[1]
        definition = remove_ini_number(definition)
        definition = remove_ini_letter(definition)
        definition = insert_end_dot(definition)
        definition = capitalize_first(definition)
        phrase = insert_end_dot(phrase)
        phrase = capitalize_first(phrase)
        phrase = insert_quotations(phrase)
        phrase = phrase.replace('Not to be confused with.','')
        phrase = phrase.replace('not to be confused with.','')
        txtphrase = phrase
        phrase = color_word(word,phrase)

        if len(txtphrase) > 60:
            continue
        if has_word_in_phrase_definition(word,phrase,definition):
            if search_in_list(uniq_phrases, phrase) == False:
                definitiontrs = yandex.get_data(definition)
                phrasetrs = yandex.get_data(txtphrase)
                uniq_phrases.append(phrase)
                lst_phrases.append({
                    'definition':definition+'<BR>'+definitiontrs,
                    'phrase':'<b>'+phrase+'</b><BR><i>'+phrasetrs+'</i>'})

def get_phrases_kdic(div_translations,word,lst_phrases,uniq_phrases,uniq_translations,country,lang):
    kdict = div_translations.find('section', attrs={"data-src" : "kdict"})
    if kdict is not None:
        results = kdict.find_all('span', class_='illustration')
        for result in results:
            phrase = result.get_text()
            translate = result.parent.find('span', attrs={"class":"trans","lang":country})
            if translate is None:
                translate = result.parent.find('span', attrs={"class":"trans","lang":lang})
            definition = result.parent.findAll(text=True, recursive=False)
            definition = " ".join(definition)
            definition = remove_dust(definition)
            definition = capitalize_first(definition)
            txt_translate = ''
            if translate is not None:
                txt_translate = translate.get_text().strip()
            if txt_translate == '' and definition is None:
                continue
            phrase = capitalize_first(phrase.strip())
            phrase = insert_end_dot(phrase)
            phrase = insert_quotations(phrase)
            phrase = remove_end_ponctuations(phrase)
            phrase = phrase.replace('Not to be confused with.','')
            phrase = phrase.replace('not to be confused with.','')
            txtphrase = phrase
            phrase = color_word(word,phrase)
            if len(txtphrase) > 60:
                continue
            if has_uniq_phrase_translation(uniq_phrases, phrase, uniq_translations, txt_translate):
                uniq_translations.append(txt_translate)
                uniq_phrases.append(phrase)
                if has_colored_word(word,phrase) == False:
                    phrase = color_word(word[:-1],phrase)
                    if has_color(phrase) == False:
                        phrase = color_word(word[:-2],phrase)

                if has_word_in_phrase_definition(word,phrase,definition):
                    if txt_translate != '':
                        definitiontrs = yandex.get_data(definition)
                        phrasetrs = yandex.get_data(txtphrase)
                        lst_phrases.append({
                            'definition':"".join(definition)+'<BR>'+definitiontrs,
                            'phrase':f' <b>{phrase}</b> '+emphasie_text(txt_translate)+'<BR><i>'+phrasetrs+'</i>'})

def get_phrases_rHouse(dictionaries,word,lst_phrases,uniq_phrases,uniq_translations,country,lang):
    rHouse = dictionaries.find('section', attrs={"data-src" : "rHouse"})
    if rHouse is not None:
        results = rHouse.find_all('span', class_='illustration')
        for result in results:
            phrase = result.get_text()
            translate = result.parent.find('span', attrs={"class":"trans","lang":country})
            if translate is None:
                translate = result.parent.find('span', attrs={"class":"trans","lang":lang})
            definition = result.parent.findAll(text=True, recursive=False)
            definition = " ".join(definition)
            definition = remove_dust(definition)
            definition = capitalize_first(definition)
            txt_translate = ''
            if translate is not None:
                txt_translate = translate.get_text().strip()
            if txt_translate == '' and definition is None:
                continue
            phrase = capitalize_first(phrase.strip())
            phrase = insert_end_dot(phrase)
            phrase = insert_quotations(phrase)
            phrase = remove_end_ponctuations(phrase)
            phrase = phrase.replace('Not to be confused with.','')
            phrase = phrase.replace('not to be confused with.','')
            txtphrase = phrase
            phrase = color_word(word,phrase)
            if len(txtphrase) > 60:
                continue
            if has_uniq_phrase_translation(uniq_phrases, phrase, uniq_translations, txt_translate):
                uniq_translations.append(txt_translate)
                uniq_phrases.append(phrase)
                if has_colored_word(word,phrase) == False:
                    phrase = color_word(word[:-1],phrase)
                    if has_color(phrase) == False:
                        phrase = color_word(word[:-2],phrase)

                if has_word_in_phrase_definition(word,phrase,definition):
                    definitiontrs = yandex.get_data(definition)
                    phrasetrs = yandex.get_data(txtphrase)
                    lst_phrases.append({
                        'definition':"".join(definition)+'<BR>'+definitiontrs,
                        'phrase':f' <b>{phrase}</b> '+emphasie_text(txt_translate)+'<BR><i>'+phrasetrs+'</i>'})

def get_simple_translations(div_translations,lst_translations,country,lang):
    simple_trans = div_translations.find('section', attrs={"class" : "simpleTrans"})
    if simple_trans is not None:
        terms = simple_trans.find('div', attrs={"lang" : country})
        if terms is None:
            terms = simple_trans.find('div', attrs={"lang" : lang})
        if terms is not None:
            simple_translations = terms.find_all('a')
            txt_trs = ''
            for trs in simple_translations:
                txt_trs += trs.get_text()+', '
            if len(simple_translations) > 0:
                lst_translations.append(txt_trs[:-2])
        
def get_kdict_translations(div_translations,word,lst_translations,country):
    kdict = div_translations.find('section', attrs={"data-src" : "kdict"})
    if kdict is not None:
        for child in kdict.descendants:
            child_text = ''
            if type(child) == Tag:
                child_text = child.get_text().replace('\n','').strip()
            if child.name == 'h2' and child_text == word:
                child_text = remove_abrv(child_text)
                lst_translations.append(f'<b>{child_text}</b>')
            elif child.name == 'i':
                if is_identification(child_text):
                    continue
                child_text = remove_abrv(child_text)
                lst_translations.append(f'<b>{child_text}</b>')
            elif child.name == 'b':
                if is_identification(child_text):
                    continue
                child_text = remove_abrv(child_text)
                lst_translations.append(f'<b>{child_text}</b>')
            else:
                if type(child) == Tag:
                    if child.has_attr('lang') and child.has_attr('class'):
                        if child['class'][0] == 'trans' and child['lang'] == country:
                            lst_translations.append(f'{child_text}')

def get_hc_mlt_translations(div_translations,lst_translations,lang):
    #it seems the section "SimpleTranslations" is enough, all translations there, are coming from here, and others dictionaries
    hc = div_translations.find('section', attrs={"data-src" : "hc_mlt"})
    if hc is not None:
        for child in hc.descendants:
            child_text = ''
            if type(child) == Tag:
                if child.has_attr('lang') and child.has_attr('class'):
                    if child['class'][0] == 'trans' and child['lang'] == lang:
                        child_text = child.get_text().strip()
                        lst_translations.append(f'{child_text}')

def get_hcPhrase(div_translations,word,lst_phrases,country,lang):
    hc = div_translations.find('section', attrs={"data-src" : "hcPhrase"})
    if hc is not None:
        phrase = ''
        phrase_tr = ''
        for child in hc.descendants:
            child_text = ''
            if type(child) == Tag:
                child_text = child.get_text().strip()
                if child.has_attr('class') and child['class'][0] == 'illustration':
                    phrase = child_text
                    if has_colored_word(word,phrase) == False:
                        phrase = color_word(word[:-1],phrase)
                        if has_color(phrase) == False:
                            phrase = color_word(word[:-2],phrase)
                    phrase = insert_end_dot(phrase)
                    phrase = f'<b>"{phrase}"</b>'
                if child.has_attr('lang') and child.has_attr('class'):
                    if child['class'][0] == 'trans':
                        if child['lang'] == lang or child['lang'] == country:
                            phrase_tr = child_text
                            phrase_tr = phrase_tr.replace(' → ','')
                            phrase_tr = phrase_tr.replace('→ ','')
                            phrase_tr = phrase_tr.replace('→','')
                            phrase_tr = insert_end_dot(phrase_tr)
                            phrase_tr = f'<i>"{phrase_tr}"</i>'
                if phrase!='' and phrase_tr!='':
                    lst_phrases.append({'definition':'','phrase':phrase+'<BR>'+phrase_tr})
                    phrase = ''
                    phrase_tr = ''

def has_word_in_phrase_definition(word,phrase,definition):
    return has_colored_word(word,phrase) or definition.find(word)>-1

def has_uniq_phrase_translation(uniq_phrases, phrase, uniq_translations, txt_translate):
    return search_in_list(uniq_phrases, phrase) == False and search_in_list(uniq_translations, txt_translate) == False

def search(word, lang, country):
    definitions_hc = []
    definitions_hm = []
    definitions_house = []
    lst_phrases = []
    lst_translations = []
    uniq_translations = []
    uniq_phrases = []
    with requests.Session() as session:
        source = session.get(f'https://www.thefreedictionary.com/{word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")

        hc_dict = soup.find('section', attrs={"data-src" : "hc_dict"})
        definition_in_dictionary(hc_dict,definitions_hc)
        american = soup.find('section', attrs={"data-src" : "hm"})
        definition_in_dictionary(american,definitions_hm)
        rHouse = soup.find('section', attrs={"data-src" : "rHouse"})
        definition_in_dictionary(rHouse,definitions_house)

        house = House()
        ipa = house.select(rHouse,word)

        dictionaries = soup.find('div', attrs={"id" : "Definition"})
        get_phrases_rHouse(dictionaries,word,lst_phrases,uniq_phrases,uniq_translations,country,lang)
        if dictionaries is None:
            return ['','','','']

        div_translations = soup.find('div', attrs={"id" : "Translations"})

        if div_translations is not None:
            get_hcPhrase(div_translations,word,lst_phrases,country,lang)
            get_phrases_kdic(div_translations,word,lst_phrases,uniq_phrases,uniq_translations,country,lang)

            get_simple_translations(div_translations,lst_translations,country,lang)
            #get_kdict_translations(div_translations,word,lst_translations,country)
            #get_hc_mlt_translations(div_translations,lst_translations,lang)

        if len(lst_phrases) < 5:
            get_phrases_from_dic(word,dictionaries,uniq_phrases,lst_phrases)

    lst_phrases = lst_phrases[:6]

    lst_phrases = generate_phrases_index(lst_phrases)

    all_definitions = join_all_definitions(definitions_hc, definitions_hm, definitions_house)
    txt_all_definitions = '<br>'.join(all_definitions)
    txt_all_definitions = txt_all_definitions[5:]

    lst_translations = remove_identifications(lst_translations)

    return [' '.join(lst_translations), txt_all_definitions, ipa, '<br><br>'.join(lst_phrases)]


def remove_abrv(txt):
    txt = txt.replace(' etc ','').replace(' eg ','').replace('especially ','')
    if txt.endswith('etc'):
        txt = txt.replace('etc','')
    if txt.endswith('eg'):
        txt = txt.replace('eg','')
    if txt.endswith('especially'):
        txt = txt.replace('especially','')
    return txt

#print(search('allowance','pt','br'))
