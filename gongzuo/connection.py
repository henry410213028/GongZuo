
from datetime import date
from gongzuo.config import (
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DATABASE,
)
from sqlalchemy import create_engine, engine
import sqlalchemy


def get_mysql_engine_raw():
    dburi = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"
    engine = create_engine(dburi)
    return engine


def get_mysql_engine():
    dburi = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    engine = create_engine(dburi)
    return engine


def get_mysql_conn():
    engine = get_mysql_engine()
    conn = engine.connect()
    return conn


def mysql_transaction(sql_query):
    engine = get_mysql_engine()
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for sql in sql_query:
                conn.execute(sqlalchemy.text(sql))
            trans.commit()
        except:
            trans.rollback()
            persist_sql(sql_query)
            raise


def persist_sql(sql_query):
    with open(f"{date.today()}.sql", "a", encoding="utf-8") as f:
        f.write("\n".join(sql_query))
