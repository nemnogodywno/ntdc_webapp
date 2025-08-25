"""
SQLAlchemy интеграция для дополнительных запросов к базе данных
Этот файл демонстрирует, как можно использовать SQLAlchemy вместе с Django
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decouple import config
import logging

logger = logging.getLogger(__name__)

# Настройка подключения к PostgreSQL через SQLAlchemy
DATABASE_URL = f"postgresql://{config('DB_USER', default='postgres')}:{config('DB_PASSWORD', default='password')}@{config('DB_HOST', default='localhost')}:{config('DB_PORT', default='5432')}/{config('DB_NAME', default='webapp_db')}"

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL, echo=config('DEBUG', default=True, cast=bool))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Получить сессию базы данных SQLAlchemy"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Ошибка создания сессии БД: {e}")
        db.close()
        raise

def get_user_statistics():
    """Пример использования SQLAlchemy для получения статистики пользователей"""
    try:
        with SessionLocal() as session:
            # Общее количество пользователей
            total_users = session.execute(
                text("SELECT COUNT(*) FROM accounts_customuser")
            ).scalar()

            # Количество администраторов
            admin_users = session.execute(
                text("""
                    SELECT COUNT(*) FROM accounts_customuser 
                    WHERE user_type = 'admin' OR is_staff = true OR is_superuser = true
                """)
            ).scalar()

            # Активные пользователи (вошедшие за последние 30 дней)
            active_users = session.execute(
                text("""
                    SELECT COUNT(*) FROM accounts_customuser 
                    WHERE last_login >= NOW() - INTERVAL '30 days'
                """)
            ).scalar()

            return {
                'total_users': total_users,
                'admin_users': admin_users,
                'active_users': active_users
            }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return {
            'total_users': 0,
            'admin_users': 0,
            'active_users': 0
        }

# Пример функции для выполнения сложных запросов
def get_users_by_registration_date():
    """Получить пользователей, сгруппированных по дате регистрации"""
    try:
        with SessionLocal() as session:
            result = session.execute(
                text("""
                    SELECT 
                        DATE(date_joined) as registration_date,
                        COUNT(*) as user_count
                    FROM accounts_customuser
                    GROUP BY DATE(date_joined)
                    ORDER BY registration_date DESC
                    LIMIT 30
                """)
            )
            return [{'date': row[0], 'count': row[1]} for row in result.fetchall()]
    except Exception as e:
        logger.error(f"Ошибка получения данных регистрации: {e}")
        return []
