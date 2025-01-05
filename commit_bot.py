#!/usr/bin/env python3
import os
import random
import datetime
import time
import schedule
import subprocess
import logging
import logging.handlers
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# --------------------------
# Configuration
# --------------------------
REPO_PATH = "/home/ubuntu/github-commit-bot"
MIN_COMMITS_RANDOM_DAY = 6
MAX_COMMITS_RANDOM_DAY = 24
COMMIT_FILE_NAME = "commit-log.txt"

# SNS Settings
SNS_REGION = "us-east-1"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:266735828641:github-commit-bot-alerts"

# Logging Config
LOG_FILE = "/home/ubuntu/github-commit-bot/commit-bot.log"

# Globals
current_random_day = None
current_week_number = None

# Set up rotating file logging
logger = logging.getLogger("CommitBot")
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5_000_000, backupCount=3
)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def send_sns_alert(subject, message):
    """
    Publish a message to the SNS topic
    (only called if a fatal error occurs).
    """
    try:
        sns_client = boto3.client("sns", region_name=SNS_REGION)
        sns_client.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
        logger.info("SNS alert sent: %s", subject)
    except (BotoCoreError, ClientError) as e:
        logger.error("Failed to send SNS alert: %s", e)

def get_current_week_number():
    """Return the ISO week number of today's date."""
    return datetime.date.today().isocalendar()[1]

def pick_new_random_day():
    """Pick a new random day for multiple commits (0=Mon,...,6=Sun)."""
    return random.randint(0, 6)

def do_commit_action(commit_message):
    """
    Perform a commit and push to GitHub.
    Raise an exception if something fails, so we can catch it and notify via SNS.
    """
    timestamp = datetime.datetime.now().isoformat()
    file_path = os.path.join(REPO_PATH, COMMIT_FILE_NAME)

    # Append a line so there's always something to commit
    with open(file_path, "a") as f:
        f.write(f"{timestamp} - {commit_message}\n")

    logger.info("Performing commit: %s", commit_message)

    # Run git commands; check=True raises a CalledProcessError on failure
    subprocess.run(["git", "-C", REPO_PATH, "add", "commit-log.txt", "commit-bot.log"], check=True)
    subprocess.run(["git", "-C", REPO_PATH, "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "-C", REPO_PATH, "push"], check=True)

    logger.info("Commit and push successful: %s", commit_message)

def schedule_today_commits():
    """
    Determine if today is the multiple-commit day.
    If so, schedule multiple commits at random times; otherwise, schedule one commit.
    """
    global current_random_day

    today_weekday = datetime.datetime.today().weekday()  # Monday=0, Sunday=6
    schedule.clear()
    if today_weekday == current_random_day:
        number_of_commits = random.randint(MIN_COMMITS_RANDOM_DAY, MAX_COMMITS_RANDOM_DAY)
        logger.info("Today is multi-commit day: scheduling %d commits.", number_of_commits)
        for i in range(number_of_commits):
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                do_commit_action, commit_message=(f"{datetime.datetime.now().isoformat()} - Multiple commit #{i+1}")
            )
    else:
        logger.info("Today is single-commit day.")
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
            do_commit_action, commit_message=(f"{datetime.datetime.now().isoformat()} - Daily single commit")
        )

def daily_reset():
    """
    Runs once per day (00:01). Check if we have a new week; if so, pick a new multi-commit day.
    Then schedule today's commits.
    """
    global current_random_day, current_week_number

    new_week_number = get_current_week_number()
    if current_week_number is None or new_week_number != current_week_number:
        current_week_number = new_week_number
        current_random_day = pick_new_random_day()
        logger.info("New week. random_day set to %d (0=Mon, 6=Sun).", current_random_day)

    schedule_today_commits()

def main():
    logger.info("Commit Bot starting up...")

    try:
        global current_random_day, current_week_number

        # Initialize
        current_week_number = get_current_week_number()
        current_random_day = pick_new_random_day()
        logger.info("Initial random_day: %d, week_number: %d",
                    current_random_day, current_week_number)

        # Schedule a daily reset at 00:01
        schedule.every().day.at("00:01").do(daily_reset)

        # Run an immediate reset in case script starts mid-day
        daily_reset()

        # Main loop
        while True:
            schedule.run_pending()
            time.sleep(30)

    except Exception as e:
        logger.error("Unhandled exception: %s", e, exc_info=True)
        # Send an alert ONLY on failure
        send_sns_alert("GitHub Commit Bot Failure", f"Unhandled exception: {e}")
        #raise  # Re-raise so systemd (in a future step) can restart the service
        return

if __name__ == "__main__":
    main()
