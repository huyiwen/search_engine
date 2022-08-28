"""Day2 Retrieve all pages from internet"""

import json
import re
import os
from os.path import splitext
from queue import Queue
from time import sleep
from random import random
from datetime import datetime
from typing import Iterable, List, Set

from urllib.parse import urlparse
from pipe import where

from Day1 import url2str, get_all_links, html2pure, tokenize


class FileSaver:

    def __init__(self, directory: str):
        self.count = 0
        self.directory = directory
        self.mapping = {}

    def __enter__(self):
        return self

    def save_file(self, html: str, url: str):
        print(f'({self.count})', end='')
        base_name = urlparse(url)[2][1:]
        if base_name == '':
            ext = '.htm'
        else:
            _, ext = splitext(base_name)

        with open(os.path.join(self.directory, str(self.count) + ext), 'w', encoding='utf-8') as f:
            f.write(html)

        text = tokenize(html2pure(html))
        with open(os.path.join(self.directory, str(self.count) + '.txt'), 'w', encoding='utf-8') as f:
            f.writelines(text)

        self.mapping[url] = self.count

        self.count += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        with open(datetime.now().strftime('%Y-%b-%d_%H-%M-%S.json'), 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f)


def bfs(base_url: str, maxsize=10, directory: str = 'saved_pages') -> Iterable[str]:
    q = Queue(maxsize=maxsize)
    q.put(base_url)
    added: Set[str] = set()

    with FileSaver(directory) as fs:
        while not q.empty():
            
            # process current link
            try:
                url = q.get_nowait()
            except:
                page = None
                url = None
            else:
                sleep(0.05)  # pa chong xie de hao, lao fan chi de zao
                page = url2str(url)

            if page is None or url is None:
                print('Error: {url}')
                continue

            fs.save_file(page, url)
            print(f'[{q.qsize()}] Current page: {url}')

            # retrieve new links
            added.add(url)
            links: Set[str] = set(
                get_all_links(page, url) | where(lambda x: not x.endswith('pdf')) | where(lambda x: re.search('ruc.edu', urlparse(x)[1]))
            )
            links -= added
            for l in links:
                if q.full():
                    break
                print(f'  + {l}')
                q.put(l)
                added.add(l)
        
    return added

if __name__ == '__main__':
    link = input('base url: ') or 'http://hqjt.ruc.edu.cn/'
    bfs(link, maxsize=0)
