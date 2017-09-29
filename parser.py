import re
import time
import itertools
from lxml.html import parse
from collections import Counter
from multiprocessing import Pool
from lxml.html.clean import clean
from urllib.request import urlopen


RE_WORDS = re.compile("[\w'-]+")


class Timer:

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(exc_value)
        else:
            print('Время выполнения: {:.3f} сек.'.format(time.time() - self.start))


def get_page_words(url):
    page = parse(urlopen(url)).getroot()
    clean(page)
    # Возможно это какой-то баг в lxml, но без замены &nbsp на пробел, парсер пропускает этот спец символ в одном месте
    raw_text = page.text_content().replace('&nbsp', ' ')
    words = RE_WORDS.findall(raw_text)
    return [word.lower() for word in words]


with Timer():
    pool = Pool()
    words = []
    main_page = parse(urlopen('https://www.socialquantum.com/')).getroot()
    links = main_page.xpath('//a')  # можно через iterlinks, но не так читаемо и менее надежно
    urls = set([url.get('href') for url in links if 'socialquantum.com' in url.get('href')])
    print('#### Обработанные ссылки ####\n')
    for url in urls:
        print(url)
    words = pool.map(get_page_words, urls)
    pool.close()
    pool.join()
    words = list(itertools.chain(*words))
    unique_words = Counter(words)
    print('\n#### Уникальные слова ####\n')
    for word, count in unique_words.items():
        print(f'{word}: {count}')
    max_word = max(unique_words, key=lambda k: unique_words[k] if len(k) > 6 else False)
    print(f'\nCамое часто употребимое слово: {max_word} - {unique_words[max_word]} раз\n')
