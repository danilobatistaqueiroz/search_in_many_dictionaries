import requests
from bs4 import BeautifulSoup
from .basic import html_headers, convert_lang

def search(word, abrv_target, lang_source, lang_target):
    lang_source = convert_lang(lang_source)
    lang_target = convert_lang(lang_target)
    lst_definitions = []
    with requests.Session() as session:
        source = session.get(f'https://{abrv_target}.bab.la/dicionario/{lang_source}-{lang_target}/{word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")
        quick_results = soup.find_all('div', class_='quick-result-overview')
        count = 0
        for result in quick_results:
            lst_txt = result.get_text().split('\n')
            lst_txt = [x for x in lst_txt if x]
            if abrv_target.upper() in lst_txt:
                div_term = result.find_previous('div', class_='quick-result-option')
                if div_term is not None:
                    term = div_term.find('a', class_='babQuickResult').get_text()
                    count+=1
                    lst_txt.remove(abrv_target.upper())
                    if term == word:
                        term = f'<b>{term}</b>'
                    lst_definitions.append('<u>'+term+'</u>:'+','.join(lst_txt))
    return ['. '.join(lst_definitions),'','','','']


#print(search('milk','pt','english','portuguese'))