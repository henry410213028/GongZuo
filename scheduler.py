
import time
from apscheduler.schedulers.background import BackgroundScheduler
from gongzuo.logger import logging
from gongzuo.db.model import create_table
from gongzuo.finder import finder


def main():
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")
    scheduler.add_job(
        id="find_job_task",
        func=finder.main,
        trigger="cron",
        hour="23",
        minute="30",
        day_of_week="mon-sun",
    )
    logging.info("Start Scheduling")
    scheduler.start()


if __name__ == "__main__":
    create_table()
    main()
    while True:
        time.sleep(600)