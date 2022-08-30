import os

from tqdm import tqdm

from process import html2pure

def save_pure(direcotry: str):
    for i in tqdm(os.listdir(direcotry)):
        if not i.endswith('.htm'):
            continue
        filename = i[:-4]
        with open(os.path.join(direcotry, i), 'r', encoding='utf-8') as fi,\
                open('../pure/'+filename+'.txt', 'w', encoding='utf-8') as fo:
            fo.write(html2pure(fi.read()))

if __name__ == '__main__':
    save_pure(input('direcotry: ') or '../saved_pages')

