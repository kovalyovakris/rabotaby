import sqlite3
from typing import List
from db_load import Vacancy

def get_vacancies(db_path: str = "db.db") -> List[Vacancy]: #получает все вакансии из БД и возвращает список объектов Vacancy
    vacancies = []

    try:
        # подключаемся к базе данных
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # выполняем SQL-запрос
            cursor.execute("""
                SELECT 
                    id,
                    name, 
                    salary, 
                    company, 
                    experience, 
                    type, 
                    technologies, 
                    region, 
                    date, 
                    link 
                FROM vacancies
            """)

            # обрабатываем результаты
            for row in cursor.fetchall():
                vacancy = Vacancy(
                    name=row[1],
                    salary=row[2],
                    company=row[3],
                    experience=row[4],
                    type=row[5],
                    technologies=row[6],
                    region=row[7],
                    date=row[8],
                    link=row[9]
                )
                vacancies.append(vacancy)

    except sqlite3.Error as e:
        print(f"Ошибка при работе с SQLite: {str(e)}")
    except Exception as e:
        print(f"Общая ошибка: {str(e)}")

    return vacancies

def get_vacancy_by_name(vacancy_name: str, db_path: str = "db.db") -> Vacancy:
    #получает одну вакансию по ID из БД и возвращает объект Vacancy
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    name, 
                    salary, 
                    company, 
                    experience, 
                    type, 
                    technologies, 
                    region, 
                    date, 
                    link 
                FROM vacancies 
                WHERE name = ?
            """, (vacancy_name,))

            result = cursor.fetchone()

            if result:
                return Vacancy(
                    name=result['name'],
                    salary=result['salary'],
                    company=result['company'],
                    experience=result['experience'],
                    type=result['type'],
                    technologies=result['technologies'],
                    region=result['region'],
                    date=result['date'],
                    link=result['link']
                )

    except sqlite3.Error as e:
        print(f"Ошибка при работе с SQLite: {str(e)}")
        return None
    except Exception as e:
        print(f"Общая ошибка: {str(e)}")
        return None