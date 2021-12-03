
import re
import pandas as pd
from sqlalchemy import text
from flask import Flask, render_template, request
from gongzuo.connection import get_mysql_engine


app = Flask(__name__, static_folder="static")
engine = get_mysql_engine()


@app.route("/jobs/")
def list_jobs():

    sql = f"""
    SELECT
    j.job_id AS `JobId`,
    j.name AS `JobName`,
    c.company_id AS `CompanyId`,
    c.company_name AS `CompanyName`,
    d.description AS `JobDescription`,
    d.salary AS `Salary`,
    STR_TO_DATE(d.appear_date, '%Y-%m-%d') AS `AppearDate`
    FROM JOB j
    LEFT JOIN COMPANY c ON j.company_id = c.company_id
    LEFT JOIN DETAIL d ON j.job_id = d.job_id
    ORDER BY `AppearDate` DESC, `Salary` DESC
    LIMIT 20;
    """

    data_df = pd.read_sql(text(sql), con=engine)
    data_dict = data_df.to_dict("records")

    return render_template(
        "search.html",
        jobs=data_dict,
        job_count=len(data_dict),
    )


@app.route("/jobs/search/")
def search_jobs():

    job = request.args.get("job")
    company = request.args.get("company")
    start_date = request.args.get("start_date") # 2021-12-01
    end_date = request.args.get("end_date") # 2021-12-31

    sql = f"""
    SELECT
    j.job_id AS `JobId`,
    j.name AS `JobName`,
    c.company_id AS `CompanyId`,
    c.company_name AS `CompanyName`,
    d.description AS `JobDescription`,
    d.salary AS `Salary`,
    STR_TO_DATE(d.appear_date, '%Y-%m-%d') AS `AppearDate`
    FROM JOB j
    LEFT JOIN COMPANY c ON j.company_id = c.company_id
    LEFT JOIN DETAIL d ON j.job_id = d.job_id
    HAVING `JobName` LIKE '%{job}%' AND `CompanyName` LIKE '%{company}%'
    """

    if start_date:
        sql = sql + f"AND `AppearDate` >= DATE('{start_date}')"

    if end_date:
        sql = sql + f"AND `AppearDate` < DATE('{end_date}')"

    data_df = pd.read_sql(text(sql), con=engine)
    data_dict = data_df.to_dict("records")

    return render_template(
        "search.html",
        jobs=data_dict,
        job_count=len(data_dict),
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
