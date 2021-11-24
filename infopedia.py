import requests
from bs4 import BeautifulSoup
from .basic import html_headers, convert_lang, blur_color_text

def search(word, abrv_target, lang_source, lang_target):
    lang_source = convert_lang(lang_source)
    lang_target = convert_lang(lang_target)
    lst_pronunciations = []
    lst_definitions = []
    with requests.Session() as session:
        source = session.get(f'https://www.infopedia.{abrv_target}/{lang_source}-{lang_target}/{word}', headers=html_headers).text
        soup = BeautifulSoup(source, "html.parser")
        quick_results = soup.find_all('div', attrs={"data-hyperlink":lang_source+"-"+lang_target})
        for result in quick_results:
            pronun = result.find('div', class_='dolEntradaVverbetePronuncia')
            txt_pronun = pronun.find('div', class_='dolEntradaVverbetePronunciaInfo').get_text()
            lst_pronunciations.append(txt_pronun)
            definitions = result.find_all('div', class_='dolCatgramAceps')
            for definition in definitions:
                rows = definition.find_all('div', class_='dolAcepsRow')
                for row in rows:
                    txt_num = ''
                    def_num = row.find('div', class_='dolAcepsNum')
                    if def_num is not None:
                        txt_num = def_num.get_text()
                    def_text = row.find('div', class_='dolAcepsRightCell')
                    descr1 = def_text.find('span', class_='dolSubacepTbvar')
                    descr2 = def_text.find('span', class_='dolSubacepTbdom')
                    descr3 = def_text.find('span', class_='dolSubacepTbreg')
                    translations = def_text.find_all('span', class_='dolAcepsSubacep')
                    all_translations = []
                    for translation in translations:
                        all_translations.append(translation.get_text())
                    row_text = ''
                    descriptions = []
                    if descr1 is not None:
                        descriptions.append(descr1.get_text())
                    if descr2 is not None:
                        descriptions.append(descr2.get_text())
                    if descr3 is not None:
                        descriptions.append(descr3.get_text())
                    row_text = blur_color_text('<u><b>'+' '.join(descriptions)+'</b></u>')
                    row_text=txt_num+' '+row_text+' '
                    row_text+=''.join(all_translations)
                    lst_definitions.append(row_text)
    txt_definitions = '<BR>'.join(lst_definitions)
    txt_definitions = '<div>'+txt_definitions+'</div>'
    return [txt_definitions,'',','.join(lst_pronunciations),'','']


#print(search('naive','pt','english','portuguese'))