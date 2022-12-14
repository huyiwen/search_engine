"""Build index with tf-idf"""

import ast
import os
import re
from math import sqrt
from collections import defaultdict
from typing import Optional, List, Union, Collection, Iterable, Tuple
from datetime import datetime
import time

import torch
import pandas as pd
import numpy as np
from tqdm import tqdm
from pipe import Pipe, select, where, take
from pandas import DataFrame, lreshape


DOC_COLUMNS = ['keyword', 'docid']
TF_COLUMNS = ['keyword', 'size']
FILENAME = datetime.now().strftime('../index/index%Y-%b-%d_%H-%M-%S.pth')


@Pipe
def build_dataframe(iterable):
    for doc, idx in iterable:
        df = DataFrame(doc, columns=['keyword'])
        df['docid'] = idx
        yield df


def get_scores(source: Iterable[Tuple[Iterable[str], int]], save: bool = True) -> DataFrame:
    """
    Args:
        source: documents or queries
    """
    tf = pd.concat(source | build_dataframe, sort=False)
    tf['docid'] = tf['docid'].astype('uint16')
    n = int(tf[['docid']].max()) + 1
    log_n = np.log(n)

    # print('Term Frequency')
    tf = tf.groupby(['keyword', 'docid'], as_index=False).size().rename(columns={'size': 'tf'}, copy=False)
    tf['tf'] = tf[['tf']].transform(lambda x: np.log10(x) + 1).astype('float32')
    print(tf.describe())
    print(tf.set_index('keyword').loc['核算'])

    # print('Inverse Document Frequency')
    idf = tf.groupby('keyword', as_index=False).size().rename(columns={'size': 'idf'})
    idf[['idf']] = idf[['idf']].agg(lambda x: log_n - np.log(x)).astype('float32')
    idf_factors = idf.idf.values[tf.keyword.factorize(sort=True)[0]]
    print(idf.describe())
    print(idf.set_index('keyword').loc['海军'])
    del idf

    # print('L2 Norm')
    l2norm = tf.rename(columns={'tf': 'l2norm'})
    l2norm['l2norm'] = l2norm.groupby('docid')[['l2norm']].transform(lambda x: x ** 2)
    l2norm = l2norm.groupby('docid')[['l2norm']].agg('sum').agg('sqrt').transform(np.log2)
    l2norm_factors = l2norm.l2norm.values[tf.docid.factorize(sort=True)[0]]
    print(l2norm.loc[78])
    print(l2norm.describe())
    del l2norm

    # print('TF-IDF Score')
    tf = tf.rename(columns={'tf': 'score'})
    # print(f' * l2norm_factors {l2norm_factors.shape}, {l2norm_factors.dtype}')
    tf['score'] = tf.score.values / l2norm_factors
    del l2norm_factors
    # print(f' * idf_factors {idf_factors.shape}, {idf_factors.dtype}')
    tf['score'] = tf.score.values * idf_factors
    del idf_factors

    if save:
        print(f'Save: {FILENAME}')
        torch.save(tf, FILENAME)
        if os.path.islink('index.pth'):
            os.remove('index.pth')
            os.symlink(FILENAME, 'index.pth')

    return tf


@Pipe
def read_keywords(iterable, direcotry):
    for fn in iterable:
        with open(os.path.join(direcotry, fn), 'r', encoding='utf-8') as f:
            yield (f.readlines() | select(lambda x: x.strip()), int(fn[:-4]))


def build_index(directory: str = '../saved_pages', quick_test: int = 0, batch: int = 500):
    """Build index (keyword, docid) pairs for every pages.

    Args:
        directory: the directory that saves the text files
        quick_test: only take the front x files
        batch: batch size

    Returns:
        dict: term freq  (keyword, docid) -> tf
        dict: doc freq  keyword -> tf
        np.ndarray: doc l2  docid -> len
    """
    # get keyword files
    kw_files = os.listdir(directory) | where(lambda x: x.endswith('.txt'))
    if quick_test > 0:
        kw_files = kw_files | take(quick_test)

    return get_scores(tqdm(kw_files) | read_keywords(directory), save=not bool(quick_test))


def load_index():
    return torch.load('../search_engine/index.pth')


def main():
    sc = build_index(quick_test=0)


if __name__ == '__main__':
    main()
    
