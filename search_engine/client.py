import json
import requests
import getpass
from urllib.parse import urljoin

# Your Search Engine Function
from query import Query

base_url = 'http://112.126.92.245:8080/'

def input_idx():
    idx = input('idx: ') or '2021201719'
    # maybe some restrictions
    return idx

def input_passwd():
    passwd = getpass.getpass('passwd for final submission: ') or '123456'
    return passwd

def login(idx, passwd):
    url = urljoin(base_url, 'login')
    r = requests.post(url, data={'idx': idx, 'passwd': passwd})
    r_dct = eval(r.text)
    queries = r_dct['queries']
    if r_dct['mode'] == 'illegal':
        raise ValueError('illegal password!')
    print(f'{len(queries)} queries.')
    return queries

def send_ans(idx, passwd, urls):
    url = urljoin(base_url, 'mrr')
    r = requests.post(url, data={'idx': idx, 'passwd': passwd, 'urls': json.dumps(urls)})
    r_dct = eval(r.text)
    if r_dct['mode'] == 'illegal':
        raise ValueError('illegal password!')
    return r_dct['mode'], r_dct['mrr']

def main():
    idx = input_idx()
    passwd = input_passwd()
    queries = login(idx, passwd)

    q = Query()
    tot_urls = []
    for query in queries:
        urls = q.query(query)
        tot_urls.append(urls)

    mode, mrr = send_ans(idx, passwd, tot_urls)
    print(f'MRR@20: [{mrr}], [{mode}] mode')

if __name__ == '__main__':
    main()
