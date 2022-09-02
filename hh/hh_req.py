from pprint import pprint
from requests import get
import re
from collections import Counter
from json import dump as jdump
from pycbrf import ExchangeRates


currency = ExchangeRates() # курсы валют
def req():
    #  ввод интересующей вакансии
    vacancy_name = input('Введите название вакансии: ')
    #vacancy_area = input('Введите регион поиска: ')
    #vacancy_currency = input('Введите валюту зарплаты: ')
    url = 'https://api.hh.ru/vacancies'

    #params = {'text': vacancy_name, 'area': vacancy_area, 'currency': vacancy_currency}
    params = {'text': vacancy_name}
    result_response = get(url=url, params=params).json()

    count_pages = result_response['pages']
    count_vacancy_on_page = len(result_response['items'])

    result = {
            'keywords': vacancy_name,
            'count': count_vacancy_on_page}

    salary = {'from': [], 'to': []}
    skills = []

    limit_pages = int(input(f'сколько страниц обработать (всего {count_pages})?:'))
    for page in range(count_pages):
        if page >= limit_pages:
            break
        else:
            print(f"Обрабатывается страница {page + 1} из {limit_pages}")
        p = {'text': vacancy_name,
             'page': page}
        ress = get(url=url, params=p).json()
        all_count = len(ress['items'])
        result['count'] += all_count
        for res in ress['items']:
            skls = set()
            res_full = get(res['url']).json()
            pp = res_full['description']
            pp_re = re.findall(r'\s[A-Za-z-?]+', pp)
            its = set(x.strip(' -').lower() for x in pp_re)
            for sk in res_full['key_skills']:
                skills.append(sk['name'].lower())
                skls.add(sk['name'].lower())
            for it in its:
                if not any(it in x for x in skills):
                    skills.append(it)
            if res_full['salary']:
                code = res_full['salary']['currency']
                if currency[code] is None:
                    code = 'RUR'
                k = 1 if code == 'RUR' else float(currency[code].value)
                salary['from'].append(k * res_full['salary']['from'] if res['salary']['from'] else k * res_full['salary']['to'])
                salary['to'].append(k * res_full['salary']['to'] if res['salary']['to'] else k*res_full['salary']['from'])
    sk2 = Counter(skills)
    up = sum(salary['from']) / len(salary['from'])
    down = sum(salary['to']) / len(salary['to'])
    result.update({'down': round(up, 2),
                   'up': round(down, 2)})
    add = []
    count_competitions = int(input('Сколько компетенций выводить?'))
    for name, count in sk2.most_common(count_competitions):
        add.append({'name': name,
                    'count': count,
                    'percent': round((count / result['count'])*100, 2)})
    result['requirements'] = add
    pprint(result)
    with open('result.json', mode='w') as f:
        jdump([result], f)
