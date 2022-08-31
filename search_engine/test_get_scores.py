from build_index import get_scores

def main():
    print(get_scores([['人大', '幼儿园', '坚持', '文化', '建园'], ['人大', '副总经理', '杨建国']], save=False))


if __name__ == '__main__':
    main()

