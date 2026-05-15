import sqlite3
import os

def create_db():
    db_name = 'tournament.db'
    sql_file = 'init_db.sql'

    # Видаляємо стару базу, якщо вона є, щоб створити чисту
    if os.path.exists(db_name):
        os.remove(db_name)
        print("🗑️ Стара база видалена.")

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Читаємо та виконуємо SQL скрипт
        with open(sql_file, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
        
        # Додаємо тестовий турнір, щоб база не була порожньою
        cursor.execute("""
            INSERT INTO Tournaments (title, description, status, min_team_size, max_team_size)
            VALUES (?, ?, ?, ?, ?)
        """, ("Перший Хакатон 2026", "Тестовий турнір для розробки", "registration", 2, 5))

        conn.commit()
        print(f"✅ База '{db_name}' успішно створена з усіма 8 таблицями!")
        print("🚀 Додано тестовий турнір.")

    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_db()