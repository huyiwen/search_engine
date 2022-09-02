import os

from tqdm import tqdm

from process import html2pure, tokenize

def save_pure(iterable, direcotry):
    for i in tqdm(iterable):
        if not i.endswith('.htm'):
            continue
        filename = i[:-4]
        with open(os.path.join(direcotry, i), 'r', encoding='utf-8') as fi,\
                open('../pure/'+filename+'.txt', 'w', encoding='utf-8') as fo:
            fo.write(html2pure(fi.read()))


def save_tokenized(iterable, direcotry):
    for i in tqdm(iterable):
        if not i.endswith('.htm'):
            continue
        filename = i[:-4]
        with open(os.path.join(direcotry, i), 'r', encoding='utf-8') as fi,\
                open(os.path.join(direcotry, filename+'.txt'), 'w', encoding='utf-8') as fo:
            fo.write('\n'.join(tokenize(html2pure(fi.read()))))

if __name__ == '__main__':
    m = input('[p]ure or [t]okenize: ')
    if m == 'p':
        print('pure file will be saved to ../pure/')
    elif m == 't':
        print('tokenized file will be saved  to ../saved_pages/')
    else:
        exit(1)

    f = input('direcotry/file of original html file: ') or '../saved_pages'
    if os.path.isfile(f):
        fs = [f]
        f = os.path.dirname(f)
    else:
        fs = os.listdir(f)

    if m == 'p':
        save_pure(fs, f)
    elif m == 't':
        save_tokenized(fs, f)


