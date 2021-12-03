
from sqlalchemy import create_engine, event, Column, DateTime, NVARCHAR, Integer, Float, func  
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from gongzuo.config import MYSQL_DATABASE
from gongzuo.connection import get_mysql_engine


engine = get_mysql_engine()
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class JOB(Base):
    __tablename__ = 'JOB'
    job_no = Column(Integer, nullable=False, unique=True, primary_key=True)  # 職缺編號
    job_id = Column(NVARCHAR(10), nullable=False, unique=True, primary_key=True)  # 職缺代號
    name = Column(NVARCHAR(200), nullable=False)  # 職缺名稱
    company_id = Column(NVARCHAR(10), nullable=False)  # 公司代號


class COMPANY(Base):
    __tablename__ = 'COMPANY'
    company_id = Column(NVARCHAR(50), nullable=False, unique=True, primary_key=True)  # 公司代號
    company_name = Column(NVARCHAR(100), nullable=False, primary_key=True)  # 公司名稱
    company_addr = Column(NVARCHAR(100), nullable=True)  # 工作地址
    lon = Column(Float, nullable=True)  # 經度
    lat = Column(Float, nullable=True)  # 緯度


class DETAIL(Base):
    __tablename__ = 'DETAIL'
    job_no = Column(Integer, nullable=False, unique=True, primary_key=True)  # 職缺編號
    job_id = Column(NVARCHAR(10), nullable=False, unique=True, primary_key=True)  # 職缺代號
    description = Column(NVARCHAR(5000), nullable=False)  # 描述
    appear_date = Column(NVARCHAR(10), nullable=False)  # 更新日期
    apply_num = Column(Integer, nullable=False)  # 應徵人數
    type = Column(Integer, nullable=True)  # 職缺類型
    education = Column(NVARCHAR(50), nullable=True)  # 學歷
    period = Column(NVARCHAR(50), nullable=True)  # 經驗年份
    salary = Column(NVARCHAR(50), nullable=True)  # 薪資描述
    salary_high = Column(Integer, nullable=True)  # 薪資最高
    salary_low = Column(Integer, nullable=True)  # 薪資最低
    tags = Column(NVARCHAR(50), nullable=True)  # 標籤


def create_db():
    from gongzuo.connection import get_mysql_engine_raw
    engine = get_mysql_engine_raw()
    with engine.connect() as conn:
        conn.execute("commit")
        conn.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE};")


def create_table():
    Base.metadata.create_all(engine)
