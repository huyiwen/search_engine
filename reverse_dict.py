import json

if __name__ == '__main__':
    decoder = json.JSONDecoder()
    with open('2022-Aug-27_17-30-52.json', 'r', encoding='utf-8') as f:
        url2idx = decoder.decode(f.read())

    idx2url = dict()
    for url, idx in url2idx.items():
        idx2url[idx] = url

 
    with open('idx2url.json', 'w', encoding='utf-8') as f:
        json.dump(idx2url, f)

