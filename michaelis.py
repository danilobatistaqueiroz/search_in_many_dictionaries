import requests
from bs4 import BeautifulSoup
from .basic import html_headers, convert_lang

def remove_title(word, content):
  start_title = content.find('<es>')
  if start_title >= 0:
    end_title = content.find('</es>')
    title = content[start_title:end_title+5]
    if title.replace('.','').strip().lower()==f'<es>{word}</es>':
      content = content[:start_title]+content[end_title+5:]
  start_title = content.find('<e1>')
  if start_title >= 0:
    end_title = content.find('</e1>')
    title = content[start_title:end_title+5]
    title = title.replace('.','').strip().lower()
    if title==f'<e1>{word}</e1>':
      content = content[:start_title]+content[end_title+5:]
    if title==f'<e1>{word}1</e1>':
      content = content[:start_title]+content[end_title+5:]
    if title==f'<e1>{word}2</e1>':
      content = content[:start_title]+content[end_title+5:]
  return content

def translation_for_same_word(word, content):
  content = content.replace('.','').lower()
  word = word.lower()
  if content.find(f'<el>{word}</el>') >= 0:
    return True
  if content.find(f'<el>{word}1</el>') >= 0:
    return True
  if content.find(f'<el>{word}2</el>') >= 0:
    return True
  if content.find(f'<es>{word}</es>') >= 0:
    return True
  return False

def remove_start_end_BR(content):
  while content[:5]=='<br/>':
      content = content[5:]
      content = content.strip()
  while content[-5:]=='<br/>':
      content = content[:-5]
      content = content.strip()
  return content

def search(word, lang_source, lang_target):
    with requests.Session() as session:
        source = session.get(f'https://michaelis.uol.com.br/moderno-ingles/busca/{lang_source}-{lang_target}-moderno/{word}/', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")
        notFound = soup.get_text().find('O verbete não foi encontrado.')
        if notFound > 0:
          return ['','','','','']
        content = soup.find('div', attrs={'id':'content'})
        content = str(content)
        content = content.replace('Ouça a pronúncia','')
        content = content.replace('<sx>Expressões</sx>','<br/><br/><sx><b>Expressões</b></sx><br/>')
        content = content.replace(f'<e1>{word}</e1><br/>','').replace(f'<es>{word}</es><br/>','')
        #content = content.replace('<cg>n</cg><br/>','').replace('<cg>vt+vi</cg><br/>','')
        content = content.replace('<ex>','<ex><b>').replace('</ex>','</b></ex>')
        content = content.replace('<ra>Amer</ra>','<ra><font color="#c7c7c7"><i>Amer</i></font></ra>')
        content = content.replace('<ra>Brit</ra>','<ra><font color="#c7c7c7"><i>Brit</i></font></ra>')
        content = content.strip()
        i = content.find('<button class="hidden audio_button"')
        if i > 0:
          f = content.find('</button>',i)
          if f > 0:
            content = content[:i]+content[f+9:]
        i = content.find('id="content"')
        if i > 0:
          verbetediv = '<div class="verbete bs-component">'
          f = content.find(verbetediv,i)
          if f > 0:
            content = content[f+len(verbetediv):]
            p = content.rfind('</div></div>')
            content = content[:p]
        content = content.strip()
        if translation_for_same_word(word, content) == False:
          return ['','','','']
        content = remove_start_end_BR(content)
        content = remove_title(word, content)
        content = remove_start_end_BR(content)
        
    return [content,'','','','']


#print(search('taurus','ingles','portugues'))