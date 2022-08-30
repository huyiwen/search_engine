from spider import get_all_links
from json import JSONDecoder
from os.path import splitext

decoder = JSONDecoder()
with open('../json/2022-Aug-30_19-51-57.json', 'r', encoding='utf-8') as f:
    mapping = decoder.decode(f.read())
while True:
    file = input('html file: ')
    idx = splitext(file)[0]
    with open('../saved_pages/' + file, 'r', encoding='utf-8') as f:
        html = f.read()
    print(list(get_all_links(html, mapping[idx])))

