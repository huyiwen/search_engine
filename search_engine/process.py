"""Process
- extract all the links and convert them into absoulte ones
- extract all the text from title and paragraphs, and then tokenize them"""

import re
from typing import Iterable, Set

import pkuseg
import jieba
from bs4 import BeautifulSoup
from pipe import where, select


def html2pure(html: str) -> str:
    """Remove html tags."""
    soup = BeautifulSoup(html, 'lxml')
    # filtration = {'script', 'style'}
    # contents = (soup.head, soup.body) | where(lambda x: x is not None) | select(lambda x: x.contents) | traverse \
    #                                   | where(lambda x: x.name not in filtration)
    # pure = '\n'.join(tag.get_text().strip() for tag in contents)
    regex = re.compile('row.*|wx|wb|footer|name|current|title|.*menu.*|breadcrumb')
    filteration = []
    filteration.extend(soup.find_all('div', {'class': regex}))
    for div in filteration:
        div.decompose()
    pure = soup.get_text()
    pure = re.sub(r' {2,}', ' ', pure)
    pure = re.sub(r'\n{2,}', '\n', pure)
    return pure

def get_stopwords(file: str = '/Users/huyiwen/Corpora/stopwords/hit_stopwords.txt') -> Set[str]:
    with open(file, 'r', encoding='utf-8') as f:
        stopwords = f.readlines() | select(lambda x: x.strip('\n'))
    return set(stopwords)




def tokenize(text: str, filterate_stopwords: bool = True, chinese: bool = True, digits: bool = False, alphabets: bool = False)\
        -> Iterable[str]:
    """remove all the characters other than alphabets, chinese characters and numbders from text and then
    tokenize the text."""
    stopwords = get_stopwords()
    pattern = r'[^ '
    if chinese:
        pattern += r'\u4e00-\u9fa5'
    if digits:
        pattern += r'^0-9'
    if alphabets:
        pattern += r'^A-Z^a-z'
    pattern += r']'

    processed = jieba.cut_for_search(re.sub(pattern, ' ', text)) | select(lambda x: x.strip())\
                    | where(lambda x: len(x) > 1)
    if filterate_stopwords:
        processed = processed | where(lambda x: x not in stopwords)
    return processed


def main():
    
    if input('Test stopwrods (y/[n]): ') == 'y':
        print(get_stopwords())

    link = input('link or file (default: http://www.ruc.edu.cn/): ') or 'http://www.ruc.edu.cn/'
    with open(link, mode='r') as f:
        page = f.read()

    assert page is not None
    pure = html2pure(page)
    yn = True if input('filterate stopwords (y/[n]):') == 'y' else False
    pure = tokenize(pure, filterate_stopwords=yn)
    pure = ' '.join(pure)
    

    print(pure)

