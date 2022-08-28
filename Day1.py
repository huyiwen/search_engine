"""Day 1
- extract all the links and convert them into absoulte ones
- extract all the text from title and paragraphs, and then tokenize them"""

import requests
import re
from typing import List, Iterable, Optional, Set

import jieba
from urllib.parse import urljoin
from url_normalize import url_normalize
from bs4 import BeautifulSoup, Tag
from pipe import dedup, traverse, where, select, chain
from fake_useragent import UserAgent

def url2str(url: str, max_trial=5, timeout=1) -> Optional[str]:
    """Retrieve page into string."""
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;"
                  "q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "cloes"
    }
    r = None
    while max_trial > 0 and r is None:
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=timeout)
            if r.status_code != 200:
                r = None
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            r = None
            max_trial -= 1
    if r is None:
        return None
    r.encoding = r.apparent_encoding
    return r.text

def html2pure(html: str) -> str:
    """Remove html tags."""
    soup = BeautifulSoup(html, 'lxml')
    # filtration = {'script', 'style'}
    # contents = (soup.head, soup.body) | where(lambda x: x is not None) | select(lambda x: x.contents) | traverse \
    #                                   | where(lambda x: x.name not in filtration)
    # pure = '\n'.join(tag.get_text().strip() for tag in contents)
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

    processed = jieba.lcut(re.sub(pattern, '', text)) | select(lambda x: x.strip())\
                    | where(lambda x: bool(x))
    if filterate_stopwords:
        processed = processed | where(lambda x: x not in stopwords)
    return processed

def get_all_links(html: str, link: str) -> Iterable[str]:
    """get all absolute links on page."""
    soup = BeautifulSoup(html, 'lxml')
    raw_links = soup.find_all('a', href=True) | select(lambda x: x.attrs.get('href'))
    abs_links = (
            raw_links | where(lambda x: not x.startswith('http')) | select(lambda x: url_normalize(urljoin(link, x))),
            raw_links | where(lambda x: x.startswith('http'))
            ) | chain | where(lambda x: not re.search('mailto|javascript|pdf', x)) | dedup
    return abs_links

if __name__ == '__main__':
    
    if input('Test stopwrods (y/[n]): ') == 'y':
        print(get_stopwords())

    link = input('link or file (default: http://www.ruc.edu.cn/): ') or 'http://www.ruc.edu.cn/'
    if link.startswith('http'):
        page = url2str(link)
    else:
        with open(link, mode='r') as f:
            page = f.read()

    assert page is not None
    pure = html2pure(page)
    yn = True if input('filterate stopwords (y/[n]):') == 'y' else False
    pure = tokenize(pure, filterate_stopwords=yn)
    pure = ' '.join(pure)
    
    links = list(get_all_links(page, link))

    print(pure)
    print(links)

