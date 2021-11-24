import requests
from bs4 import BeautifulSoup
from .basic import html_headers, convert_lang, capitalize_first, color_word, blur_color_text
from . import yandex

def remove_link(html):
  html = html.replace('</a>','')
  while True:
    open_a = html.find('<a ')
    if open_a > 0:
      close_a = html.find('>',open_a)
      html = html[:open_a] + html[close_a+1:]
    else:
      break
  return html


def text_treatment(txt):
    txt = txt.replace('\n','')
    txt = txt.replace('\n',' ').replace('  ',' ').strip()
    return txt

def rem_duplications_sort(out):
    if out['ipas'] is not None:
        out['ipas'] = list(set(out['ipas']))
        out['ipas'].sort()
    else:
        out['ipas'] = []
    if out['phrases'] is not None:
        out['phrases'] = list(set(out['phrases']))
        out['phrases'].sort()
    else:
        out['phrases'] = []

def generate_indexes(out):
    if out['phrases'] is not None:
        out['phrases'] = generate_index(out['phrases'])

def generate_index(lst):
    cnt=0
    lsttmp = []
    for item in lst:
        cnt+=1
        lsttmp.append(f'{cnt:02}. {item}')
    return lsttmp

def find_dictionary(word, soup, dic):
    txt_ipas = []
    txt_phrases = []
    div_definitions = soup.select(dic)
    for div_definition in div_definitions:
        senses = div_definition.find_all('div', class_='sense')
        for sense in senses:
            phrase = sense.find('div', class_='quote')
            if phrase is None:
                phrase = sense.find('span', class_='quote')
            if phrase is not None:
                phrase_definition = phrase.find_previous('div', class_='def')
                text_phrase = phrase.get_text().strip()
                text_phrase = text_treatment(text_phrase)
                text_phrase = capitalize_first(text_phrase)
                trs_phrase = yandex.get_data(text_phrase)
                text_phrase = color_word(word,text_phrase)
                txt_phrase_def = ''
                if phrase_definition is not None:
                    txt_phrase_def = phrase_definition.get_text()
                    txt_phrase_def = text_treatment(txt_phrase_def)
                    txt_phrase_def = capitalize_first(txt_phrase_def)
                    trs_phrase_def = yandex.get_data(txt_phrase_def)
                    trs_phrase_def = blur_color_text(trs_phrase_def)
                    txt_phrase_def = blur_color_text(txt_phrase_def)
                phrasedef = f'{txt_phrase_def}<BR>{trs_phrase_def}<BR>'
                phrasetxt = f'<b>"{text_phrase}"</b><BR><i>"'+trs_phrase+'"</i><BR>'
                txt_phrases.append(phrasedef+phrasetxt)
    sp_ipas = soup.find_all('span', class_=['pron', 'type-'])
    for sp_ipa in sp_ipas:
        texts = sp_ipa.text.replace('  ',' ').split(',')
        for text in texts:
            txt_ipas.append(text.strip())
    
    return {'ipas':txt_ipas, 'phrases':txt_phrases}

def search(word):
    with requests.Session() as session:
        source = session.get(f'https://www.collinsdictionary.com/us/dictionary/english/{word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")

        #txt = soup.prettify()
        #writer = open('./collins_miscreant.txt','w')
        #writer.write(txt)
        #writer.close()
        #return
        #reader = open('./collins_miscreant.txt','r')
        #alltxt = reader.read()
        #reader.close()
        #soup = BeautifulSoup(alltxt, "html.parser")

        out = find_dictionary(word, soup, 'div.definitions.american')
        if len(out['phrases']) == 0:
            out = find_dictionary(word, soup, 'div.cobuild.am')
            if len(out['phrases']) == 0:
                out = find_dictionary(word, soup, 'div.cobuild.ced')
    rem_duplications_sort(out)
    generate_indexes(out)

    quotes = soup.find_all('span', class_='quote')
    lstquotes = []
    for quote in quotes:
      txtquote = quote.get_text().strip()
      if txtquote.find(word) > 0:
        txtquote = color_word(word, txtquote)
        lstquotes.append(f'<b>{txtquote}</b><br>')

    definitions = soup.find_all('div', class_='def')
    lstdefinitions = []
    for definition in definitions:
      sense = definition.find_parent("div", class_="sense")
      html_def = str(definition)
      if sense is not None:
        label = sense.find("span", class_="lbl")
        if label is not None:
          label = label.get_text().strip().lower()
          if label == 'archaic':
            html_def = ' <b>ARCHAIC</b> '+html_def
      hom = definition.find_parent("div", class_="hom")
      if hom is not None:
        grp = hom.find("span", class_="gramGrp")
        txt_grp = grp.get_text().strip()
        html_def = blur_color_text(txt_grp) + html_def
      html_def = text_treatment(html_def)
      html_def = remove_link(html_def)
      lstdefinitions.append(html_def)
    txtdefinitions = ''
    if len(lstdefinitions) > 0:
      txtdefinitions = '<BR>'.join(lstdefinitions)
      if len(lstquotes) > 0:
        txtquotes = '<BR>'.join(lstquotes)
        txtdefinitions+'<BR><b>QUOTES</b><BR><BR>'+txtquotes
    txtipas = ''
    if len(out['ipas']) > 0:
      out['ipas'] = list(set(out['ipas']))
      txtipas = ', '.join(out['ipas'])
    txtphrases = ''
    if len(out['phrases']) > 0:
      txtphrases = '<BR>'.join(out['phrases'])
    return ['', txtdefinitions,txtipas,txtphrases]

#print(search('miscreant'))