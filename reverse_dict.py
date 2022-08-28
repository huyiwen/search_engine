import json


decoder = json.JSONDecoder()


def get_idx2url() -> dict:
    with open('idx2url.json', 'r', encoding='utf-8') as f:
        raw = decoder.decode(f.read())
    idx2url = {}
    for k, v in raw.items():
        idx2url[int(k)] = v
    return idx2url


if __name__ == '__main__':
    with open('2022-Aug-27_17-30-52.json', 'r', encoding='utf-8') as f:
        url2idx = decoder.decode(f.read())

    idx2url = dict()
    for url, idx in url2idx.items():
        idx2url[idx] = url

 
    with open('idx2url.json', 'w', encoding='utf-8') as f:
        json.dump(idx2url, f)

