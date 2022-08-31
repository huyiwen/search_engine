"""Build index with tf-idf"""

import ast
import os
import re
from math import sqrt
from collections import defaultdict
from typing import Optional, List, Union, Collection, Iterable, Tuple
from datetime import datetime

import torch
import pandas as pd
import numpy as np
from tqdm import tqdm
from pipe import select, where, take
from pandas import DataFrame


DOC_COLUMNS = ['keyword', 'docid']
TF_COLUMNS = ['keyword', 'size']
FILENAME = datetime.now().strftime('index%Y-%b-%d_%H-%M-%S.pth')


def build_index(directory: str = '../saved_pages', quick_test: int = 0, batch: int = 500)\
        -> Tuple[dict, dict, np.ndarray]:
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
    kw_files = sorted(kw_files)

    tf = DataFrame(columns=DOC_COLUMNS)
    tf_temp = DataFrame(columns=DOC_COLUMNS)
    count = 0

    for file in tqdm(kw_files):

        # read keywords
        count += 1
        idx = int(file[:-4])
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            kws = f.readlines() | select(lambda x: x.strip())

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

    # TF
    #   get term freq and log n
    tf = tf.groupby(['keyword', 'docid'], as_index=False).size()
    log_n = np.log10(int(tf[['docid']].max()))
    #   calc log tf
    tf['tf'] = tf[['size']].apply(lambda x: np.log10(x) + 1)
    #tf = tf.drop('size', axis=1).set_index('keyword')
    #   build mapping "(keyword, docid)" -> tf (sorted by tf)
    # tf_dict = tf.set_index(['keyword', 'docid']).T.to_dict('records')[0]
    # tf_dict = dict(sorted(tf_dict.items(), key=lambda x: x[1]))

    # DF
    #   get doc freq
    df = tf.groupby('keyword', as_index=False).size()
    #   calc idf
    df[['df']] = df[['size']].agg(lambda x: log_n - np.log10(x))
    #   build mapping "keyword -> df" (sorted by df)
    df_dict = df[['keyword', 'df']].set_index('keyword').T.to_dict('records')[0]
    df_dict = dict(sorted(df_dict.items(), key=lambda x: x[1]))

    # DL
    #   get doc len
    dl = tf
    #   calc L2 norm
    dl['dl'] = dl.groupby('docid')[['tf']].transform(lambda x: x ** 2)
    dl = dl.groupby('docid')[['tf']].agg('sum').agg('sqrt')
    #    build list mapping "docid -> len"
    for idx in np.setdiff1d(np.arange(int(dl.index.max())+1), dl.index):
        dl.loc[idx] = 0
        print(idx)
    doc_len = dl.sort_index().values

    if not quick_test:
        torch.save((tf, df_dict, doc_len), FILENAME)

    return tf, df_dict, doc_len


def load_index():
    return torch.load('index.pth')


def main():
    tf, df, doc_len = build_index(quick_test=0)
    #torch.save(tf, 'tf.pth')
    #torch.save(df, 'df.pth')
    #torch.save(doc_len, 'doc_len.pth')

    #tf, df, doc_len = torch.load('tf.pth'), torch.load('df.pth'), torch.load('doc_len.pth')
    print(len(tf))
    print(len(df))
    print(doc_len)


    # query2idx = pairs.to_dict()['docid']
    # idx2url = get_idx2url()
    # q = Query(query2idx, idx2url)
    # while(1):
    #     q.query(query=input('query: '), method='vanilla')


if __name__ == '__main__':
    main()
    
