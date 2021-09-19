from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_email


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_email,
                      trigger="cron",
                      hour="09",
                      minute="00",
                      second="00")
    # alternate
    # scheduler.add_job(schedule_email,
                      # "interval",
                      # hours=24)
    # debugging
    # scheduler.add_job(schedule_email,
                      # "interval",
                      # seconds=10)
    scheduler.start()
