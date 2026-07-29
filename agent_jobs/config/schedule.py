import os

# Cron trigger kwargs for apscheduler's CronTrigger, default daily 08:00 local.
DEFAULT_HOUR = int(os.environ.get("AGENT_JOBS_SCHEDULE_HOUR", "8"))
DEFAULT_MINUTE = int(os.environ.get("AGENT_JOBS_SCHEDULE_MINUTE", "0"))
