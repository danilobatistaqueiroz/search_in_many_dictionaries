import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString
from .basic import html_headers, convert_lang, capitalize_first, color_word, insert_end_dot, emphasie_text

def remove_start_end_BR(content):
  while content[:5]=='<br/>':
      content = content[5:]
      content = content.strip()
  while content[-5:]=='<br/>':
      content = content[:-5]
      content = content.strip()
  return content

def search(word, lang_source, lang_target):
    lang_source = convert_lang(lang_source)
    lang_target = convert_lang(lang_target)
    lst_definitions = []
    lst_examples = []
    lst_expressions = []
    with requests.Session() as session:
        source = session.get(f'https://www.linguee.com.br/{lang_source}-{lang_target}/search?source=auto&query={word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")

        definitions = soup.find_all('a', class_='dictLink featured')
        for result in definitions:
            lst_definitions.append(result.get_text())

        examples = soup.find_all('div', class_='example')
        cnt = 0
        for result in examples:
            cnt+=1
            lst_txt = result.get_text().split('—')
            example = insert_end_dot(capitalize_first(lst_txt[0].strip()))
            example = color_word(word,example)
            translated = insert_end_dot(capitalize_first(lst_txt[1].strip()))

            term = result.parent.parent.find('h3').find('a')
            term = "".join([t for t in term.contents if type(t)==NavigableString])
            term = term.strip()

            lst_examples.append(f'<b>"{example}"</b> {emphasie_text(term)} ')
            lst_examples.append(f'<i>"{translated}"</i> <br>')

        cnt=0
        inexact = soup.find('div', class_='example_lines inexact')
        if inexact is not None:
            lemmas = inexact.find_all('div', class_='lemma singleline')
            for lemma in lemmas:
                cnt+=1
                taglemma = lemma.find('span', class_='tag_lemma')
                dictLink_source = taglemma.find('a', class_='dictLink')

                lemmacontent = lemma.find('div', class_='lemma_content')
                dictLink2_target = lemmacontent.find('a', class_='dictLink')

                example = insert_end_dot(dictLink_source.get_text())
                translated = insert_end_dot(dictLink2_target.get_text())

                if example.find(word) > -1:
                    example = color_word(word,example)
                    lst_expressions.append('<b>"'+example+'"</b>')
                    lst_expressions.append('<i>"'+translated+'"</i> <br>')
                expressions = '<br>'.join(lst_expressions)
                expressions = remove_start_end_BR(expressions)

    phrases = '<br>'.join(lst_examples)[:-4]
    return ['', ','.join(lst_definitions), '', phrases, '', expressions]

#print(search('streak','english','portuguese'))