import sqlite3
import csv
import os
import subprocess

CSV_FILE = "vacancies_rabota_by.csv"
DB_FILE = "db.db"

class Vacancy:
    def __init__(self, name, salary, company, experience, type, technologies, region, date, link):
        self.name = name
        self.salary = salary
        self.company = company
        self.experience = experience
        self.type = type
        self.technologies = technologies
        self.region = region
        self.date = date
        self.link = link

    def to_dict(self): # преобразует объект класса в словарь для сохранения в бд
        return {
            "name": self.name,
            "company": self.company,
            "salary": self.salary,
            "region": self.region,
            "date": self.date,
            "experience": self.experience,
            "type": self.type,
            "technologies": self.technologies,
            "link": self.link
        }


def run_parser(): # запуск парсера
    try:
        result = subprocess.run(["python", "vacancy_parser.py"], check=True, capture_output=True, text=True)
        print("Парсер успешно выполнен:")
        if result.stderr:
            print("Ошибки парсера:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске парсера: {e}")
        print(e.stderr)
        return False
    return True


def read_csv(): # чтение данных из csv
    vacancies = []
    if not os.path.exists(CSV_FILE):
        print(f"Файл {CSV_FILE} не найден.")
        return vacancies

    with open(CSV_FILE, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            vacancy = Vacancy(
                name=row["Название вакансии"],
                company=row["Компания"],
                salary=row["Зарплата"],
                region=row["Регион"],
                date=row["Дата публикации"],
                experience=row["Опыт работы"],
                type=row["Тип занятости"],
                link=row["URL"],
                technologies=row["Требуемые технологии"]
            )
            vacancies.append(vacancy)

    return vacancies


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # создаем таблицу vacancies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            salary TEXT,
            region TEXT,
            date TEXT,
            experience TEXT,
            type TEXT,
            link TEXT,
            technologies TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_to_db(vacancies):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # очищаем существующие данные
    cursor.execute("DELETE FROM vacancies")  # затем удаляем вакансии

    # сброс id
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('vacancies', 'technologies', 'vacancy_technologies')")

    for vacancy in vacancies:
        # вставляем вакансию в таблицу
        cursor.execute("""
            INSERT INTO vacancies (name, company, salary, region, date, experience, type, link, technologies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vacancy.name,
            vacancy.company,
            vacancy.salary,
            vacancy.region,
            vacancy.date,
            vacancy.experience,
            vacancy.type,
            vacancy.link,
            vacancy.technologies
        ))

    conn.commit()
    conn.close()
    print(f"Данные сохранены в {DB_FILE}")


def start_db():
    init_db()

    print("Запуск парсера...")
    if not run_parser():
        print("Парсер завершился с ошибкой. Прерывание.")
        return

    print(f"Чтение данных из {CSV_FILE}...")
    vacancies = read_csv()

    if vacancies:
        save_to_db(vacancies)
        print(f"Сохранено {len(vacancies)} вакансий в базу данных.")
    else:
        print("Нет данных для сохранения в базу данных.")
