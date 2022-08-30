"""Day4
- tf-idf"""

import ast
import os
import re
from math import sqrt
from collections import defaultdict
from typing import Optional, List, Union, Collection, Iterable, Tuple

import torch
import pandas as pd
import numpy as np
from tqdm import tqdm
from pipe import select, where, take
from pandas import DataFrame

from Day1 import tokenize
from reverse_dict import get_idx2url


DOC_COLUMNS = ['keyword', 'docid']
TF_COLUMNS = ['keyword', 'size']


def build_index(directory: str = 'saved_pages', old_ver: bool = True, quick_test: int = 0, batch: int = 500)\
        -> Tuple[dict, dict, np.ndarray]:
    """Build index (keyword, docid) pairs for every pages.

    Args:
        directory: the directory that saves the text files
        old_ver: compatible with old version of text files (not tokenized)
        quick_test: only take the front x files
        batch: batch size

    Returns:
        dict: term freq  (keyword, docid) -> tf
        dict: doc freq  keyword -> tf
        np.ndarray: doc l2  docid -> len
    """
    if quick_test > 0:
        kw_files = os.listdir(directory) | where(lambda x: x.endswith('.txt')) | take(quick_test)
    else:
        kw_files = os.listdir(directory) | where(lambda x: x.endswith('.txt'))
    kw_files = sorted(kw_files)

    tf = DataFrame(columns=DOC_COLUMNS)
    tf_temp = DataFrame(columns=DOC_COLUMNS)
    count = 0

    for file in tqdm(kw_files):

        # read keywords
        count += 1
        idx = int(file[:-4])
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            if old_ver:
                kws = tokenize(f.read())
            else:
                kws = f.readlines()

        # get keywords
        kws = DataFrame(kws | select(lambda x: (x, idx)), columns=DOC_COLUMNS)

        # append keywords
        tf_temp = pd.concat((tf_temp, kws), sort=False)
        if count == batch:
            count = 0
            tf = pd.concat((tf, tf_temp), sort=False)
            tf_temp = DataFrame(columns=DOC_COLUMNS)

    # append rest keywords
    if count > 0:
        tf = pd.concat((tf, tf_temp), sort=False)

    # (1 + log(x)) * log(N / y)
    tf = tf.groupby(['keyword', 'docid'], as_index=False).size()
    log_n = np.log10(int(tf[['docid']].max()))
    tf['tf'] = tf[['size']].apply(lambda x: np.log10(x) + 1)
    tf = tf.drop('size', axis=1)
    tf_dict = tf.set_index(['keyword', 'docid']).T.to_dict('records')[0]  # (keyword, docid) -> tf
    tf_dict = dict(sorted(tf_dict.items(), key=lambda x: x[1]))

    df = tf.groupby('keyword', as_index=False).size()
    df[['df']] = df[['size']].agg(lambda x: log_n - np.log10(x))
    df_dict = df[['keyword', 'df']].set_index('keyword').T.to_dict('records')[0]  # keyword -> df
    df_dict = dict(sorted(df_dict.items(), key=lambda x: x[1]))

    dl = tf
    dl['dl'] = dl.groupby('docid')[['tf']].transform(lambda x: x ** 2)
    dl = dl.groupby('docid')[['tf']].agg('sum').agg('sqrt')
    doc_len = dl.values  # docid -> len

    return tf_dict, df_dict, doc_len


class Query:

    def __init__(self, query2idx: dict, idx2url: dict, doc_len: list):
        self.query2idx = defaultdict(list, query2idx)
        self.idx2url = defaultdict(lambda: 'Error: no url found', idx2url)
        self.doc_len = doc_len

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

    def vanilla(self, queries: List[str]) -> List[str]:
        queries[0] = self.query2idx[queries[0]]
        if len(queries) > 1:
            for q in queries[1:]:
                queries[0] = self._intersect(queries[0], self.query2idx[q])
        return list(self.idx2url[idx] for idx in queries[0])

    def query(self, query: str, method: str):
        query_method = getattr(self, method)
        queries = re.split(',|，', query)
        result = query_method(queries)

        print(f'{method} query={query}\n{result}')


if __name__ == '__main__':
    tf, df, doc_len = build_index(quick_test=5)
    #torch.save(tf, 'tf.pth')
    #torch.save(df, 'df.pth')
    #torch.save(doc_len, 'doc_len.pth')

    #tf, df, doc_len = torch.load('tf.pth'), torch.load('df.pth'), torch.load('doc_len.pth')
    print(len(tf))
    print(len(df))
    print(len(doc_len))


    # query2idx = pairs.to_dict()['docid']
    # idx2url = get_idx2url()
    # q = Query(query2idx, idx2url)
    # while(1):
    #     q.query(query=input('query: '), method='vanilla')


