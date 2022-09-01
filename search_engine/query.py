"""Day3
- Build index"""

import os
import re
from typing import Optional, List, Union, Collection, Iterable
from collections import defaultdict, Counter
import ast
from json import JSONDecoder
import logging
from datetime import datetime

import numpy as np
import pandas as pd
from pandas import DataFrame
from pipe import select, take, tee
import jieba
import pkuseg

from reverse_dict import get_idx2url
from build_index import load_index, get_scores
from init_logger import init_logger
from process import tokenize

FILENAME = datetime.now().strftime('query%Y-%b-%d_%H-%M-%S.log')
logger = init_logger(logging.getLogger(), FILENAME)


class Query:

    def __init__(self):
        decoder = JSONDecoder()
        with open('../json/2022-Aug-30_19-51-57.json', 'r', encoding='utf-8') as f:
            self.idx2url = decoder.decode(f.read())
        self.idx2vec = load_index().set_index('keyword')
        logger.debug(self.idx2vec.loc['养老'])
        logger.debug(self.idx2vec.loc['外籍'])
        logger.debug(self.idx2vec.loc['核算'])
        self.doc_num = int(self.idx2vec.docid.max()) + 1
        seg = pkuseg.pkuseg('news')
        #self.cutter = seg.cut
        self.cutter = tokenize

    def query(self, query: str) -> List[str]:
        queries = query.split(' ')
        q_count = len(queries)
        qt = Counter(self.cutter(query))
        pattern = '|'.join(set(queries) - set(qt.keys()))
        to_add_queries = set(qt.keys()) - set(queries)
        logger.info(f'query={query} ({q_count}) {pattern}')
        scores = np.zeros(self.doc_num)
        add = defaultdict(lambda: np.zeros_like(scores))

        for q, c in qt.items():
            intersection = self.idx2vec.index.intersection([q])

            if len(intersection) == 0:
                continue
            logger.debug(f'{q}: {c} ({intersection})')

            pairs = self.idx2vec.loc[intersection].set_index('docid') * (np.log10(c) + 1)

            top_20 = pairs[['score']].sort_values(by='score', axis=0, ascending=False).iloc[:20].rename(columns={'score': q})
            #every_scores[q] = top_20
            logger.debug(f"query scores:\n{top_20}\n")

            if q in to_add_queries:
                temp = np.zeros(self.doc_num)
                temp[pairs.index] += pairs[['score']].values.squeeze()
                scores -= temp
                add[q] += temp
            else:
                scores[pairs.index] -= pairs[['score']].values.squeeze()

        #every_scores.dropna(how='all', inplace=True)
        #logger.debug(f'every_scores:\n{every_scores}')
        #logger.debug(f'every_scores:\n{every_scores.loc[418]}')

        pages = np.argsort(scores, axis=0)[:20].squeeze().tolist()
        logger.debug(pages)
        logger.debug(sorted(scores)[:20])
        minus = defaultdict(lambda: np.zeros_like(scores))
        if pattern:
            for docid in pages:
                with open('../pure/' + str(docid) + '.txt') as f:
                    for w, c in Counter(re.findall(pattern, f.read())).items():
                        s = np.log10(c + 8)
                        minus[w][docid] -= s
                        logger.debug(s)
            for q in add:
                scores += add[q]
            for m in minus:
                scores += minus[m] * np.log10(40 / np.count_nonzero(minus[m]))

        pages = np.argsort(scores, axis=0)[:20].squeeze().tolist()
        logger.debug(sorted(scores)[:20])

        logger.debug(pages)
        pages = list(pages | select(lambda x: self.idx2url[str(x)]))
        logger.debug(pages)
             
        return pages


if __name__ == '__main__':

    q = Query()

    tsv = input('tsv ([../codes&slides/query_30.tsv]/n): ') or '../codes&slides/query_30.tsv'
    if tsv == 'n':
        while(1):
            q.query(query=input('query: ') or '项目')
    else:
        scores = []
        with open(tsv, 'r', encoding='utf-8') as f:
            line_count = 0
            for line in f.readlines():
                ans, query = line.strip().split('\t')
                output = q.query(query=query)
                line_count += 1
                score = 0
                for count, url in enumerate(output):
                    if url == ans:
                        score = (20 - count) / 20
                        break
                scores.append(score)
                logger.info(f'[{query}]: {score}')
                logger.info(f'ans: {ans}\n')
            logger.info(f'MRR@20: {sum(scores) / line_count}')
            logger.info(scores)
    logger.info(f'log: {FILENAME}')



