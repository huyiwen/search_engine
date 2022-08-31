from process import tokenize


words = [
    '老校区',
]


def test_tokenize():
    for i in words:
        print(i)
        print(' '.join(tokenize(i)))


if __name__ == '__main__':
    test_tokenize()


