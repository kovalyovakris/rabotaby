import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from urllib.parse import urljoin

# Настройки
BASE_URL = "https://rabota.by/search/vacancy"
VACANCY_BASE_URL = "https://rabota.by"
SEARCH_PARAMS = {
    "text": "программист",  # ключевое слово для поиска
    "area": 16,  # беларусь
    "page": 0  # начальная страница
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}
OUTPUT_FILE = "vacancies_rabota_by.csv"
tech_keywords = [
    r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\btypescript\b',
    r'\bc#\b', r'\bc\+\+\b', r'\bc\b', r'\bgo\b', r'\bgolang\b',
    r'\bruby\b', r'\bphp\b', r'\bswift\b', r'\bkotlin\b', r'\bscala\b',
    r'\br\b', r'\brust\b', r'\bdart\b', r'\belixir\b', r'\berlang\b',
    r'\bperl\b', r'\bhaskell\b', r'\bclojure\b', r'\bdelphi\b', r'\bobjective-c\b',
    r'\bvb\.net\b', r'\bf#\b', r'\bbash\b', r'\bpowershell\b',

    # фронтенд
    r'\bhtml\b', r'\bcss\b', r'\bsass\b', r'\bscss\b', r'\bless\b',
    r'\breact\b', r'\breact\.js\b', r'\bangular\b', r'\bangularjs\b',
    r'\bvue\b', r'\bvue\.js\b', r'\bember\b', r'\bbackbone\b', r'\bsvelte\b',
    r'\bjquery\b', r'\bd3\.js\b', r'\bredux\b', r'\bmobx\b', r'\bgraphql\b',
    r'\bapollo\b', r'\bwebpack\b', r'\bbabel\b', r'\bgulp\b', r'\bgrunt\b',
    r'\bparcel\b', r'\bjest\b', r'\bmocha\b', r'\bchai\b', r'\bcypress\b',
    r'\bselenium\b', r'\bstorybook\b', r'\bnext\.js\b', r'\bnuxt\.js\b',
    r'\bgatsby\b', r'\bthree\.js\b',

    # бэкенд
    r'\bnode\.js\b', r'\bexpress\b', r'\bnestjs\b', r'\bdjango\b',
    r'\bflask\b', r'\bfastapi\b', r'\bspring\b', r'\bspring boot\b',
    r'\bmicronaut\b', r'\bquarkus\b', r'\blaravel\b', r'\bsymfony\b',
    r'\bruby on rails\b', r'\basp\.net\b', r'\basp\.net core\b',
    r'\bphoenix\b', r'\bgin\b', r'\becho\b', r'\bfiber\b',
    r'\bkoa\b', r'\bhapi\b', r'\bsails\b', r'\bmeteor\b',

    # бд
    r'\bmysql\b', r'\bpostgresql\b', r'\bmongodb\b', r'\bredis\b',
    r'\bsqlite\b', r'\boracle\b', r'\bsql server\b', r'\bms sql\b',
    r'\bmariadb\b', r'\bcassandra\b', r'\bcouchdb\b', r'\bfirebase\b',
    r'\bfirestore\b', r'\bdynamodb\b', r'\bneo4j\b', r'\barangodb\b',
    r'\belasticsearch\b', r'\bsolr\b', r'\bhbase\b', r'\bbigquery\b',
    r'\bsnowflake\b', r'\bcosmos db\b', r'\bclickhouse\b',

    # devops и облачные технологии
    r'\bdocker\b', r'\bkubernetes\b', r'\bterraform\b', r'\bansible\b',
    r'\bpuppet\b', r'\bchef\b', r'\bjenkins\b', r'\bgitlab ci\b',
    r'\bgithub actions\b', r'\bcircleci\b', r'\btravis ci\b',
    r'\baws\b', r'\bamazon web services\b', r'\bs3\b', r'\bec2\b',
    r'\blambda\b', r'\brds\b', r'\bdynamodb\b', r'\bazure\b',
    r'\bgoogle cloud\b', r'\bgcp\b', r'\bfirebase\b', r'\bheroku\b',
    r'\bdigitalocean\b', r'\bopenstack\b', r'\bvagrant\b',
    r'\bprometheus\b', r'\bgrafana\b', r'\bsplunk\b', r'\bkibana\b',
    r'\bnew relic\b', r'\bdatadog\b',

    # мобильная разработка
    r'\breact native\b', r'\bflutter\b', r'\bionic\b', r'\bxamarin\b',
    r'\bcordova\b', r'\bcapacitor\b', r'\bswiftui\b', r'\buikit\b',

    # блокчейн
    r'\bsolidity\b', r'\bethereum\b', r'\bhyperledger\b', r'\bweb3\b',
    r'\btruffle\b', r'\bhardhat\b',

    # машинное обучение и data science
    r'\btensorflow\b', r'\bpytorch\b', r'\bkeras\b', r'\bscikit-learn\b',
    r'\bpandas\b', r'\bnumpy\b', r'\bmatplotlib\b', r'\bseaborn\b',
    r'\bopencv\b', r'\bnltk\b', r'\bspacy\b', r'\bhugging face\b',
    r'\bapache spark\b', r'\bhadoop\b', r'\bairflow\b', r'\bkafka\b',
    r'\bflink\b', r'\btableau\b', r'\bpower bi\b', r'\blooker\b',

    # другие технологии и инструменты
    r'\bgit\b', r'\bsvn\b', r'\bmercurial\b', r'\bjira\b', r'\bconfluence\b',
    r'\btrello\b', r'\basana\b', r'\bslack\b', r'\bteams\b', r'\bzoom\b',
    r'\brest\b', r'\bsoap\b', r'\boauth\b', r'\bjwt\b', r'\boauth2\b',
    r'\bopenid\b', r'\bwebsockets\b', r'\bgrpc\b', r'\bprotobuf\b',
    r'\bgraphql\b', r'\bapollo\b', r'\bnginx\b', r'\bapache\b',
    r'\brabbitmq\b', r'\bkafka\b', r'\bactivemq\b', r'\bzeromq\b',
    r'\blinux\b', r'\bunix\b', r'\bwindows server\b', r'\bmacos\b',
    r'\bvmware\b', r'\bvirtualbox\b', r'\bvpn\b', r'\bldap\b',
    r'\bactive directory\b', r'\bsaml\b', r'\boauth\b', r'\boauth2\b',

    # методологии
    r'\bagile\b', r'\bscrum\b', r'\bkanban\b', r'\bwaterfall\b',
    r'\bdevops\b', r'\bci/cd\b', r'\btdd\b', r'\bbdd\b', r'\bddd\b',

    # доп технологии
    r'\bseo\b', r'\bgoogle analytics\b', r'\bgtm\b', r'\bhotjar\b',
    r'\badobe analytics\b', r'\boptimizely\b', r'\ba/b testing\b',
    r'\bwebassembly\b', r'\bwasm\b', r'\bpwa\b', r'\bamp\b',
    r'\bblockchain\b', r'\bcryptocurrency\b', r'\bnft\b',
    r'\bar\b', r'\bvr\b', r'\bunity\b', r'\bunreal engine\b',

    # корпоративные и нишевые технологии
    r'\b1c:erp\b',
    r'\b1c\b',
    r'\bdatareon platform\b', r'\bdatareon\b',
    r'\bbitrix24\b', r'\bbitrix\b',
    r'\bt-flex plm\b', r'\bt-flex\b', r'\bplm\b',

    # версии технологий
    r'\b\.net \d+\b', r'\bpython \d+\.\d+\b', r'\bjava \d+\b',
    r'\bphp \d+\.\d+\b', r'\bnode \d+\b', r'\breact \d+\b'
]


def fetch_page(url, params=None): # загружает страницу и возвращает html
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text
    except requests.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return None


def parse_vacancies(html): # из html возвращает данные
    soup = BeautifulSoup(html, "html.parser")
    vacancies = []

    # получаем все блоки вакансий
    vacancy_blocks = soup.select("div.vacancy-info--ieHKDTkezpEj0Gsx")  # Селектор для карточек вакансий
    if not vacancy_blocks:
        print("Вакансии не найдены. Проверьте селектор или структуру страницы.")
        return vacancies

    for vacancy in vacancy_blocks:
        try:
            # название вакансии
            title_elem = vacancy.select_one("span[data-qa='serp-item__title-text']")
            title = title_elem.get_text(strip=True) if title_elem else "Не указано"
            vacancy_url_elem = vacancy.select_one("a[data-qa='serp-item__title']")
            vacancy_url = urljoin(VACANCY_BASE_URL, vacancy_url_elem["href"]) if vacancy_url_elem and vacancy_url_elem.get("href") else ""

            # зп
            salary_elem = vacancy.select_one("span.magritte-text___pbpft_3-0-32.magritte-text_style-primary___AQ7MW_3-0-32.magritte-text_typography-label-1-regular___pi3R-_3-0-32")
            salary = salary_elem.get_text(separator=' ', strip=True) if salary_elem else "Не указана"

            # работодатель
            employer_elem = vacancy.select_one("span[data-qa='vacancy-serp__vacancy-employer-text']")
            employer = employer_elem.get_text(separator=' ', strip=True)

            # город
            address_elem = vacancy.select_one("span[data-qa='vacancy-serp__vacancy-address']")
            city = address_elem.get_text(strip=True) if address_elem else "Не указано"

            # опыт работы
            experience_elem = vacancy.select_one("span[data-qa='vacancy-serp__vacancy-work-experience-between3And6']")
            experience = experience_elem.get_text(strip=True) if experience_elem else "Не указано"

            vacancies.append({
                "Название вакансии": title,
                "Зарплата": salary,
                "Компания": employer,
                "Регион": city,
                "Опыт работы": experience,
                "Тип занятости": "",
                "Требуемые технологии": "",
                "Дата публикации": "",
                "URL": vacancy_url
            })


        except Exception as e:
            print(f"Ошибка при парсинге вакансии: {e}")
            continue

    return vacancies


def parse_vacancy_page(html): # получает инфу с личной страницы вакансии
    soup = BeautifulSoup(html, "html.parser")
    vacancy_data = {}

    try:
        # тип занятости
        employment_elem = soup.select_one("p[data-qa='work-formats-text']")
        vacancy_data["Тип занятости"] = employment_elem.get_text(strip=True)[14:] if employment_elem else "Не указано"

        # технологии
        description_elem = soup.select_one("div.g-user-content")
        technologies = "Не указано"
        if description_elem:
            # извлекаем текст связанный с технологиями
            text = description_elem.get_text(strip=True).lower()
            found_tech = []
            for pattern in tech_keywords:
                if re.search(pattern, text):
                    tech_name = pattern.replace(r'\b', '').replace(r'\.', '.').replace(r'\-', '-')
                    found_tech.append(tech_name)
            technologies = "; ".join(sorted(set(found_tech))) if found_tech else "Не указано"
        vacancy_data["Требуемые технологии"] = technologies

        # дата
        date_elem = soup.select_one("p.vacancy-creation-time-redesigned")
        date = date_elem.get_text(strip=True) if date_elem else "Не указано"
        date = format_date(date)
        vacancy_data["Дата публикации"] = date

    except Exception as e:
        print(f"Ошибка при парсинге страницы вакансии: {e}")
        vacancy_data.update({
            "Тип занятости": "Не указано",
            "Требуемые технологии": "Не указано"
        })

    return vacancy_data

def format_date(date_str): # преобразование даты в норм формат (дд.мм.гггг)
    months = {
        "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
        "мая": "05", "июня": "06", "июля": "07", "августа": "08",
        "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
    }
    match = re.search(r'(\d{1,2})\s*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s*(\d{4})', date_str)
    if match:
        day, month, year = match.groups()
        return f"{int(day):02d}.{months[month]}.{year}"
    return "Не указана"

def save_to_csv(data, filename=OUTPUT_FILE): # сохраняем данные в csv
    df_data = {
        "Название вакансии": [item["Название вакансии"] for item in data],
        "Компания": [item["Компания"] for item in data],
        "Зарплата": [item["Зарплата"] for item in data],
        "Регион": [item["Регион"] for item in data],
        "Дата публикации": [item["Дата публикации"] for item in data],
        "Опыт работы": [item["Опыт работы"] for item in data],
        "Тип занятости": [item["Тип занятости"] for item in data],
        "URL": [item["URL"] for item in data],
        "Требуемые технологии": [item["Требуемые технологии"] for item in data]
    }

    df = pd.DataFrame(df_data)
    if os.path.exists(filename):
        df.to_csv(filename, mode="a", index=False, header=False, encoding="utf-8-sig")
    else:
        df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"Данные сохранены в {filename}")


def main():
    print("Сбор вакансий начат...")
    all_vacancies = []
    max_pages = 1  # количество страниц

    # парсинг блоков вакансий
    for page in range(max_pages):
        SEARCH_PARAMS["page"] = page
        print(f"Загрузка страницы поиска {page + 1}...")
        html = fetch_page(BASE_URL, SEARCH_PARAMS)
        if not html:
            print("Не удалось загрузить страницу поиска. Прерывание.")
            break

        vacancies = parse_vacancies(html)
        if not vacancies:
            print("Вакансии не найдены или конец страниц.")
            break

        # парсинг личных страниц вакансий
        for vacancy in vacancies:
            if vacancy["URL"]:
                print(f"Загрузка страницы вакансии: {vacancy['Название вакансии']}")
                vacancy_html = fetch_page(vacancy["URL"])
                if vacancy_html:
                    vacancy_data = parse_vacancy_page(vacancy_html)
                    vacancy.update(vacancy_data)
                time.sleep(0.5)  # задержка для избежания блокировки

        all_vacancies.extend(vacancies)
        time.sleep(1)  # задержка между страницами

    if all_vacancies:
        save_to_csv(all_vacancies)
        print(f"Собрано {len(all_vacancies)} вакансий.")
    else:
        print("Вакансии не собраны.")

if __name__ == "__main__":
    main()