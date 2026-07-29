from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from agent_jobs.cli.run_cmd import run
from agent_jobs.config.schedule import DEFAULT_HOUR, DEFAULT_MINUTE


def schedule() -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(run, CronTrigger(hour=DEFAULT_HOUR, minute=DEFAULT_MINUTE))
    print(f"[schedule] running once now, then daily at {DEFAULT_HOUR:02d}:{DEFAULT_MINUTE:02d} local time")
    run()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
