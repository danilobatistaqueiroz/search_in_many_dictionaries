
#document.querySelectorAll('.ex-sent').forEach((f)=>{if (f.innerText.indexOf('evens')>0) console.log(f.innerText)})
#document.querySelectorAll('div.vg').forEach((f)=>{ console.log(f.innerText) })

import requests
from bs4 import BeautifulSoup
from .basic import html_headers, emphasie_text, color_word

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

def search(word):
    with requests.Session() as session:
        source = session.get(f'https://www.merriam-webster.com/dictionary/{word}/', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")
        notFound = soup.get_text().find("The word you've entered isn't in the dictionary")
        if notFound > 0:
          return ['','','','','']
        #txt = soup.prettify()
        #writer = open('./webster_evens.txt','w')
        #writer.write(txt)
        #writer.close()
        #return
        #reader = open('./webster_evens.txt','r')
        #alltxt = reader.read()
        #reader.close()
        #soup = BeautifulSoup(alltxt, "html.parser")
        contents = soup.find_all('div', attrs={'class':'vg'})
        phrases = []
        for content in contents:
          phrase = str(content).replace('\n','').replace('</span>','</span><br>')
          if phrase.find(word) > 0:
            phrases.append(phrase)
        txtphrases = '<br>'.join(phrases)
        txtphrases = remove_link(txtphrases)
        txtphrases = color_word(word,txtphrases)

        contents = soup.find_all('div', attrs={'class':'sense'})
        senses = []
        for content in contents:
          sense = str(content).replace('\n','').replace('</span>','</span><br>')
          sense = remove_link(sense)
          senses.append(sense)
        txtsenses = '<br>'.join(senses)

    return ['',txtsenses,'',txtphrases,'']

#[translations, definitions, ipa, phrases]

print(search('clunker'))