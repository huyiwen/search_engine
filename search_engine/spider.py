"""Spider: Retrieve all pages from internet"""

import sys
import json
import re
import os
import logging
from os.path import splitext
from queue import Queue, Empty
from datetime import datetime
from typing import Iterable, List, Set, Optional

import colorama
from fake_useragent import UserAgent
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urljoin
from pipe import where, select, chain, dedup
from bs4 import BeautifulSoup
from url_normalize import url_normalize

from process import html2pure, tokenize

FILE_EXTS = ('xls', 'xlsx', 'doc', 'docx', 'pdf', 'jpg', 'png', 'gif')

filename = datetime.now().strftime('%Y-%b-%d_%H-%M-%S')
fh = logging.FileHandler('../log/'+filename+'.log')
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.addHandler(fh)


class FileSaver:

    def __init__(self, directory: str, json_file: Optional[str] = None):
        self.count = 0
        self.directory = directory
        self.mapping = {}
        self.added = set()
        self.name = filename
        self.logger = logger

        if json_file:
            with open(json_file, 'r', encoding='utf-8') as f:
                decoder = json.JSONDecoder()
                self.added = set(decoder.decode(f.read()).values())
            self.count = len(self.added)

    def __enter__(self):
        return self

    def save_file(self, html: str, url: str):
        self.logger.info(f'({self.count})')
        base_name = urlparse(url).path[1:]
        _, ext = splitext(base_name)
        if ext == '':
            ext = '.htm'

        with open(os.path.join(self.directory, str(self.count) + ext), 'w', encoding='utf-8') as f:
            f.write(html)

        page = html2pure(html)
        text = tokenize(page)
        with open(os.path.join(self.directory, str(self.count) + '.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(text))

        self.mapping[self.count] = url

        self.count += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        with open('json/'+self.name+'.json', 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f)


def url2str(url: str, max_retries=5) -> Optional[str]:
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
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=max_retries))
    s.mount('https://', HTTPAdapter(max_retries=max_retries))
    try:
        r = s.get(url, headers=headers, timeout=(6.05, 12.05))
        if r.status_code != 200:
            logger.debug(f'stauts_code: {r.status_code}')
            
            r = None
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.RequestException) as e:
        logger.debug(f'Error: {e}')
        r = None
    if r is None:
        return None

    r.encoding = r.apparent_encoding
    return r.text


def get_all_links(html: str, link: str) -> Iterable[str]:
    """get all absolute links on page."""
    soup = BeautifulSoup(html, 'lxml')
    if not link.endswith('htm') and not link.endswith('/'):
        link = link + '/index.htm'
    raw_links = list(soup.find_all('a', href=True) | select(lambda x: x.attrs.get('href')))
    abs_links = (
            raw_links | where(lambda x: not x.startswith('http')) | select(lambda x: url_normalize(urljoin(link, x))),
            raw_links | where(lambda x: x.startswith('http'))
            ) | chain | where(lambda x: not re.search('mailto|javascript|pdf', x)) | dedup
    return abs_links


def bfs(base_url: str, maxsize=10, directory: str = 'saved_pages', load: Optional[str] = None) -> Iterable[str]:

    q = Queue(maxsize=maxsize)
    q.put(base_url)
    with FileSaver(directory, load) as fs:
        while not q.empty():
            
            # process current link
            try:
                url = q.get(block=True, timeout=3)
            except Empty:
                break
            fs.logger.info(f'[{q.qsize()}] Current page: {url}')
            if not url.endswith('htm'):
                fs.logger.warning(colorama.Fore.YELLOW + f'{url}' + colorama.Fore.RESET)
            page = url2str(url, max_retries=10)

            if url is None:
                fs.logger.error(f'Url not found.')
                continue

            if page is None:
                fs.logger.warning(f'Page not found: {url}')
                continue


            fs.save_file(page, url)

            # retrieve new links
            fs.added.add(url)
            links: Set[str] = set(
                get_all_links(page, url) | where(lambda x: not x.endswith(FILE_EXTS) and not re.search(r'\$', x))\
                        | where(lambda x: re.search('hqjt.ruc.edu', urlparse(x)[1])) | select(lambda x: x[:-1] if x.endswith('/') else x)
            )
            links -= fs.added
            for l in links:
                if q.full():
                    break
                fs.logger.info(f'  + {l}')
                q.put(l, block=True, timeout=3)
                fs.added.add(l)
        
    return fs.added

if __name__ == '__main__':
    link = input('base url: ') or 'http://hqjt.ruc.edu.cn/index.htm'
    bfs(link, maxsize=0, load=input('load file: '))
