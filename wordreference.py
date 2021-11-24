from bs4 import BeautifulSoup, NavigableString
import requests
from .basic import html_headers, color_word, has_colored_word, blur_color_text, emphasie_text

all_definitions = []
all_translations = []
all_pronunciations = []
all_phrases = []

def trim_all(list):
    newlist = []
    for item in list:
        newlist.append(item.strip())
    return newlist

def remove_more_than_one_spaces(txt):
    while txt.find('  ') > -1:
        txt = txt.replace('  ',' ')
    return txt

def is_tr_in_same_section(tr):
    if tr is not None and tr.get("id") is not None:
        return False
    else:
        return True

def get_section_translations(translations, tr):
    td = tr.find("td",class_="ToWrd")
    if td is not None:
        if td.find("em") is not None:
            td.find("em").extract()
        if td.find("i") is not None:
            td.find("i").extract()
        translations.append(td.get_text().strip())

def get_section_words(words, tr):
    td = tr.find("td",class_="FrWrd")
    if td is not None:
        if td.find("em") is not None:
            td.find("em").extract()
        if td.find("i") is not None:
            td.find("i").extract()
        words.append(td.get_text().strip())

def get_section_definitions(definitions, tr):
    td = tr.find("td", class_=False)
    if td is not None:
        if isinstance(td, NavigableString)==False:
            if td.get("class") is None:
                if td.find("em") is not None:
                    td.find("em").extract()
                text = td.get_text().strip().replace('\n','').replace('BRA','').replace('POR','')
                text = text.replace('informal ','').replace('informal,','').replace(', (','(').replace('(, ','(')
                text = remove_more_than_one_spaces(text)
                text = text.replace('( )','').replace('()','')
                definitions.append(text)
        td = td.find_next_sibling("td")

def get_section_phrases(phrases, tr):
    td = tr.find("td", class_="FrEx")
    if td is not None:
        text = td.get_text().strip()
        phrases.append(f'<b>"{text}"</b>')
    td = tr.find("td", class_="ToEx")
    if td is not None:
        text = td.get_text().strip()
        phrases.append(f'<i>"{text}"</i>')

def get_all_pronunciations(soup):
    prons = soup.find_all("span",class_="pronRH tooltip pronWidget")
    prons.extend(soup.find_all("span",class_="pronWR tooltip pronWidget"))
    for pron in prons:
        if pron.get_text().find("respelling") == -1:
            pron.find("span").extract()
            all_pronunciations.append(pron.get_text().strip())

def get_all_definitions(top):
    td = top.td
    while td is not None:
        if isinstance(td, NavigableString)==False:
            if td.get("class") is None:
                if td.find("em") is not None:
                    td.em.extract()
                if td.find("i") is not None:
                    td.i.extract()
                if td.find("span",class_="dsense") is not None:
                    td.find("span",class_="dsense").extract()
                text = td.get_text().strip().replace('\n','')
                text = remove_more_than_one_spaces(text)
                all_definitions.append(text)
        td = td.find_next_sibling("td")

def get_all_translations(soup):
    tr = soup.find("tr", id=True)
    while tr is not None:
        td = tr.find("td",class_="ToWrd")
        if td is not None:
            if td.find("em") is not None:
                td.find("em").extract()
            if td.find("i") is not None:
                td.find("i").extract()
            all_translations.append(td.get_text().strip())
        tr = tr.find_next_sibling("tr")

def get_data_section(top):
    words = []
    definitions = []
    translations = []
    phrases = []
    tr = top
    same_section = True
    get_section_words(words, tr)
    get_section_definitions(definitions, tr)
    while tr is not None and same_section == True:
        get_section_translations(translations, tr)
        get_section_phrases(phrases, tr)
        tr = tr.find_next_sibling("tr")
        same_section = is_tr_in_same_section(tr)
    txt_words = ','.join(words)
    txt_definitions = ' '.join(definitions)
    txt_translations = ', '.join(translations)
    txt_phrases = '<BR>'.join(phrases)
    all_phrases.append(blur_color_text('<b>'+txt_words+'</b> '+txt_definitions)+'<BR>'+blur_color_text(txt_translations)+'<BR>'+txt_phrases+'<BR>')

def search(word, abrv_source, abrv_target):
    with requests.Session() as session:
        html = session.get(f'https://www.wordreference.com/{abrv_source}{abrv_target}/{word}', headers=html_headers).text
        soup = BeautifulSoup(html, "html.parser")
        starts = soup.find_all("tr", id=True)
    get_all_pronunciations(soup)
    get_all_translations(soup)
    for top in starts:
        get_data_section(top)
        get_all_definitions(top)
    return [', '.join(all_translations), ', '.join(all_definitions), ', '.join(all_pronunciations), '<BR>'.join(all_phrases)]

#search('pickup','en','pt')