from apscheduler.schedulers.background import BackgroundScheduler
from app.notification.notification_service import send_daily_notifications

_scheduler = None  # 🔒 singleton

def create_scheduler():
    global _scheduler

    if _scheduler and _scheduler.running:
        return _scheduler

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        send_daily_notifications,
        trigger="interval",
        seconds=60,
        id="notification_dispatcher",
        replace_existing=True,
        max_instances=1,          # 🔒 prevents overlap
        coalesce=True             # 🔒 skip missed runs
    )

    _scheduler = scheduler
    return scheduler