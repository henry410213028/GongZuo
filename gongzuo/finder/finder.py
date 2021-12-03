
import time
import random
import requests
import pandas as pd
import pymysql
import re
from datetime import datetime, date
from gongzuo.connection import mysql_transaction
from gongzuo.logger import logging


def get_header():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Referer': 'https://www.' + str(52 * 2) + '.com.tw/jobs/search/',
    }


def get_query(keyword, filter_params=None, is_sort_asc=False):
    query = f'ro=0&kwop=7&keyword={keyword}&expansionType=area,spec,com,job,wf,wktm&mode=s&jobsource=2018indexpoc'
    if filter_params:
        query += ''.join([f'&{key}={value}' for key, value, in filter_params.items()])

    sort_params = '&order=1'  # 符合度 1, 日期 2, 經歷 3, 學歷 4, 應徵人數 7, 待遇 13
    sort_params += '&asc=1' if is_sort_asc else '&asc=0'
    query += sort_params
    return query


def transform(df):
    if re.match(r"\d{8}", df['appearDate']):
        df['appear_date'] = datetime.strptime(df['appearDate'], '%Y%m%d').strftime('%Y-%m-%d')
    else:
        df['appear_date'] = str(date.today())

    df['apply_num'] = int(df['applyCnt'])
    df['company_addr'] = f"{df['jobAddrNoDesc']} {df['jobAddress']}"

    df['job_id'] = df['link']['job'].split('/job/')[-1]
    if '?' in df['job_id']:
        df['job_id'] = df['job_id'].split('?')[0]

    df['company_id'] = df['link']['cust'].split('/company/')[-1]
    if '?' in df['company_id']:
        df['company_id'] = df['company_id'].split('?')[0]

    df['description'] = df['description'].replace('\r\n', '\n').replace('\r', '\n')
    df['description'] = "".join([s for s in df['description'] if s.isprintable() or (s == '\n')])

    df['salary_high'] = int(df['salaryLow'])
    df['salary_low'] = int(df['salaryHigh'])

    if isinstance(df['tags'], list):
        df['tags'] = ",".join(df['tags'])
    else:
        df['tags'] = str(df['tags'])
    
    return df


def create_job_table(df):
    job = {
        'job_no': df['jobNo'],  # 職缺編號
        'job_id': df['job_id'],  # 職缺代號
        'name': df['jobName'],  # 職缺名稱
        'company_id': df['company_id'],  # 公司代號
    }
    return pd.Series(job)


def create_company_table(df):
    company = {
        'company_id': df['company_id'],  # 公司代號
        'company_name': df['custName'],  # 公司名稱
        'company_addr': df['company_addr'],  # 工作地址
        'lon': df['lon'],  # 經度
        'lat': df['lat'],  # 緯度
    }
    return pd.Series(company)


def create_detail_table(df):
    detail = {
        'job_no': df['jobNo'],  # 職缺編號
        'job_id': df['job_id'],  # 職缺代號
        'type': df['jobType'],  # 職缺類型
        'description': df['description'],  # 描述
        'appear_date': df['appear_date'],  # 更新日期
        'apply_num': df['apply_num'],  # 應徵人數
        'education': df['optionEdu'],  # 學歷
        'period': df['periodDesc'],  # 經驗年份
        'salary': df['salaryDesc'],  # 薪資描述
        'salary_high': df['salary_high'],  # 薪資最高
        'salary_low': df['salary_low'],  # 薪資最低
        'tags': df['tags'],  # 標籤
    }
    return pd.Series(detail)


def create_insert_update_sql(table, df):
    column = list(df.columns)
    columns = "`,`".join(column)
    sql_list = []
    for i in range(len(df)):
        row = list(df.iloc[i, :])
        value = [pymysql.converters.escape_string(str(v)) for v in row]
        values = '","'.join(value)
        update_sql = ", ".join([f'`{column[j]}` = "{str(value[j])}"' for j in range(len(column)) if str(value[j])])
        sql = f"INSERT INTO `{table}`(`{columns}`) VALUES (\"{values}\") ON DUPLICATE KEY UPDATE {update_sql};"
        sql_list.append(sql)
    return sql_list


def main(keyword="python"):
    retry_time = 3
    df = pd.DataFrame()
    total_count = 0

    url = 'https://www.' + str(52 * 2) + '.com.tw/jobs/search/list'
    filter_params = {
        'area': '6001001000,6001002000',  # (地區) 台北市,新北市
        's9': '1',  # 1,2,4,8 # (上班時段) 日班,夜班,大夜班,假日班
        's5': '0',  # 0:不需輪班 256:輪班
        'wktm': '1',  # (休假制度) 週休二日
        'isnew': '0',  # (更新日期) 0:本日最新 3:三日內 7:一週內 14:兩週內 30:一個月內
        # 'jobexp': '1,3,5,10,99',  # (經歷要求) 1年以下,1-3年,3-5年,5-10年,10年以上
        # 'newZone': '1,2,3,4,5',  # (科技園區) 竹科,中科,南科,內湖,南港
        # 'zone': '16',  # (公司類型) 16:上市上櫃 5:外商一般 4:外商資訊
        # 'wf': '1,2,3,4,5,6,7,8,9,10',  # (福利制度) 年終獎金,三節獎金,員工旅遊,分紅配股,設施福利,休假福利,津貼/補助,彈性上下班,健康檢查,團體保險
        # 'edu': '1,2,3,4,5,6',  # (學歷要求) 高中職以下,高中職,專科,大學,碩士,博士
        # 'remoteWork': '1',  # (上班型態) 1:完全遠端 2:部分遠端
        # 'excludeJobKeyword': '科技',  # 排除關鍵字
        # 'kwop': '1',  # 只搜尋職務名稱
    }
    headers = get_header()
    query = get_query(keyword=keyword, filter_params=filter_params)

    page = 1
    total_page = 999
    while page < total_page:
        params = f'{query}&page={page}'

        for i in range(retry_time):
            try:
                response = requests.get(url, params=params, headers=headers)
                logging.debug("Finish Response")
                break
            except:
                logging.warning(f"Request Error, Retry {i + 1}: {url}, {params}")

        if response.status_code != 200:
            logging.error(f"Response ({response.status_code})")
            continue

        data = response.json()

        if data['status'] != 200:
            logging.error(f"Data Error: {data['status']}, {data['statusMsg']}, {data['errorMsg']}")
            continue

        df = pd.concat([df, pd.DataFrame(data['data']['list'])], axis=0)
        total_count = int(data['data']['totalCount'])
        total_page = int(data['data']['totalPage'])

        if (page == total_page) or (total_page == 0):
            logging.debug("End of Process")
            break

        df = df.apply(transform, axis=1)
        df_job = df.apply(create_job_table, axis=1)
        df_company = df.apply(create_company_table, axis=1)
        df_detail = df.apply(create_detail_table, axis=1)

        sql_query = create_insert_update_sql("JOB", df_job) + \
            create_insert_update_sql("COMPANY", df_company) + \
            create_insert_update_sql("DETAIL", df_detail)

        mysql_transaction(sql_query)
        logging.info(f"Finish Page: {page}/{total_page}")
        page += 1
        time.sleep(random.uniform(3, 5))

    logging.info(f"Total: {total_count}")
