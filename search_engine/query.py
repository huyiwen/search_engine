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

import jieba
import numpy as np
import pandas as pd
from pandas import DataFrame
from jieba import lcut
from pipe import select, take, tee

from reverse_dict import get_idx2url
from build_index import build_index, load_index
from init_logger import init_logger

FILENAME = datetime.now().strftime('query%Y-%b-%d_%H-%M-%S.log')
logger = init_logger(logging.getLogger(), FILENAME)


class Query:

    def __init__(self, query2idx: DataFrame, idx2url: dict, doc_len: Optional[np.ndarray] = None):
        self.query2idx = query2idx.set_index('keyword')
        self.idx2url = defaultdict(lambda: 'Error: no url found', idx2url)
        self.doc_len = doc_len
        self.doc_len[self.doc_len == 0] = 1

    @staticmethod
    def _intersect(first: Collection, second: Collection) -> list:
        p1, p2 = iter(first), iter(second)
        len1, len2 = len(first), len(second)
        intersection = []

        doc1, doc2 = next(p1), next(p2)
        len1 -= 1
        len2 -= 1
        run = True

        while run:

            while doc1 == doc2:
                intersection.append(doc1)
                if len1 == 0 or len2 == 0:
                    run = False
                    break
                doc1, doc2 = next(p1), next(p2)
                len1 -= 1
                len2 -= 1

            while doc1 < doc2:
                if len1 == 0:
                    run = False
                    break
                doc1 = next(p1)
                len1 -= 1

            while doc2 < doc1:
                if len2 == 0:
                    run = False
                    break
                doc2 = next(p2)
                len2 -= 1

        return intersection

    def vanilla(self, query: str) -> List[str]:
        queries = re.split(',|，', query)
        queries[0] = self.query2idx[queries[0]]
        if len(queries) > 1:
            for q in queries[1:]:
                queries[0] = self._intersect(queries[0], self.query2idx[q])
        return list(self.idx2url[idx] for idx in queries[0])

    def tfidf(self, query: str) -> List[str]:
        qt = Counter(jieba.lcut(query))
        scores = np.zeros_like(self.doc_len)

        every_scores = DataFrame(index=range(len(scores)))
        for q, c in qt.items():
            c = np.log10(c) + 1
            intersection = self.query2idx.index.intersection([q])
            if len(intersection) == 0:
                continue
            logger.debug(f'{q}: {c} ({intersection})')
            pairs = self.query2idx.loc[intersection].set_index('docid') * c
            top_20 = pairs[['tf']].sort_values(by='tf', axis=0, ascending=False).iloc[:20].rename(columns={'tf': q})
            every_scores[q] = top_20
            logger.debug(f"query scores:\n{top_20}\n")
            scores[pairs.index] -= pairs[['tf']].values

        scores /= self.doc_len
        every_scores.dropna(how='all', inplace=True)
        logger.debug(f'every_scores:\n{every_scores}')
        logger.debug(f'every_scores:\n{every_scores.loc[418]}')
        pages = np.argsort(scores, axis=0)[:20].squeeze().tolist()
             
        return list(pages | select(lambda x: self.idx2url[str(x)]))

    def query(self, query: str, method: str) -> list:
        query_method = getattr(self, method)
        result = query_method(query)

        print(f'{method} query={query}\n{result}')
        return result

root = None


def evaluate(query: str) -> list:
    global root
    if root is None:
        tf, df, doc_len = load_index()
        decoder = JSONDecoder()
        with open('../json/2022-Aug-30_19-51-57.json', 'r', encoding='utf-8') as f:
            idx2url = decoder.decode(f.read())
        root = Query(tf, idx2url, doc_len)
    
    return root.query(query, method='tfidf')


if __name__ == '__main__':

    # tf, df, doc_len = build_index(quick_test=0)
    #print(tf)
    #print(df)
    #print(doc_len)
    tf, df, doc_len = load_index()
    logger.info("=======test=======")
    logger.info(f'tf:\n{tf.describe()}')
    logger.info(f'tf: {tf.shape}')
    logger.info(f'doc_len: {doc_len.shape}')
    decoder = JSONDecoder()
    with open('../json/2022-Aug-30_19-51-57.json', 'r', encoding='utf-8') as f:
        idx2url = decoder.decode(f.read())

    logger.info(f"docid 1: {idx2url['1']}")
    logger.info(f'log: {FILENAME}')
    logger.info("=======test=======")
    q = Query(tf, idx2url, doc_len)
    tsv = input('tsv ([../codes&slides/query_30.tsv]/n): ') or '../codes&slides/query_30.tsv'
    if tsv == 'n':
        while(1):
            q.query(query=input('query: ') or '项目', method='tfidf')
    else:
        with open(tsv, 'r', encoding='utf-8') as f:
            avg = 0.
            line_count = 0
            for line in f.readlines():
                ans, query = line.strip().split('\t')
                output = q.query(query=query, method='tfidf')
                line_count += 1
                for count, url in enumerate(output):
                    if url == ans:
                        logger.info(f'[{query}]: {(20-count)/20}')
                        logger.info(f'ans: {ans}\n')
                        avg += (20 - count) / 20
                        break
            logger.info(f'MRR@20: {avg / line_count}')



