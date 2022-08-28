"""Day3
- Build index"""

import os
import re
from typing import Optional, List, Union, Collection
from collections import defaultdict

from pipe import select, where, take
import pandas as pd
from pandas import DataFrame

from Day1 import tokenize
from reverse_dict import get_idx2url


COLUMNS = ['keyword', 'docid']


def build_index(directory: str = 'saved_pages', old_ver: bool = True, quick_test: int = 0) -> DataFrame:
    """Build index (keyword, docid) pairs for every pages.

    Args:
        directory: the directory that saves the text files
        old_ver: compatible with old version of text files (not tokenized)
    """
    if quick_test > 0:
        kw_files = os.listdir(directory) | where(lambda x: x.endswith('.txt')) | take(quick_test)
    else:
        kw_files = os.listdir(directory) | where(lambda x: x.endswith('.txt'))

    kw_docid_pairs = DataFrame(columns=COLUMNS)
    for file in kw_files:
        idx = int(file[:-4])
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            if old_ver:
                kws = tokenize(f.read())
            else:
                kws = f.readlines()
            kws = DataFrame(kws | select(lambda x: (x, idx)), columns=COLUMNS)
            kw_docid_pairs = pd.concat((kw_docid_pairs, kws), sort=False)

    kw_docid_pairs = kw_docid_pairs.sort_values(by=COLUMNS)
    assert kw_docid_pairs is not None
    return kw_docid_pairs


def build_inverted_index(pairs: DataFrame) -> DataFrame:
    return pairs.groupby('keyword')['docid'].apply(list).reset_index().set_index('keyword')


class Query:

    def __init__(self, query2idx: dict, idx2url: dict):
        self.query2idx = defaultdict(list, query2idx)
        self.idx2url = defaultdict(lambda: 'Error: no url found', idx2url)

    def _intersect(self, first: Collection, second: Collection) -> list:
        p1, p2 = iter(first), iter(second)
        len1, len2 = len(first), len(second)
        intersection = []
        while len1 > 0 and len2 > 0:
            len1 -= 1
            len2 -= 1
            doc1, doc2 = next(p1), next(p2)
            if doc1 == doc2:
                intersection.append(doc1)
            elif doc1 < doc2:
                doc1 = next(p1)
                len1 -= 1
            else:
                doc2 = next(p2)
                len2 -= 1
        return intersection

    def vanilla(self, query: str) -> List[str]:
        return list(self.query2idx[query] | select(lambda x: self.idx2url[x]))

    def query(self, query: str, method: str):
        query_method = getattr(self, method)

        queries = re.split(',|，', query)

        if len(queries) > 1:
            queries = sorted(queries, key=lambda x: len(x))
            for q in queries[1:]:
                queries[0] = self._intersect(queries[0], q)

        result = query_method(query[0])
        print(f'{method} query="{query}" {result}')


if __name__ == '__main__':
    pairs = build_index(quick_test=5)
    pairs = build_inverted_index(pairs)
    pairs.to_csv('index.csv')
    query2idx = pairs.to_dict()['docid']
    idx2url = get_idx2url()
    q = Query(query2idx, idx2url)
    while(1):
        q.query(query=input('query: '), method='vanilla')


