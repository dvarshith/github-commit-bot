# **GitHub Commit Bot**
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
<br/>
Ever wished you had a neat little bot to keep your GitHub streak alive—or just to have some fun with automated commits? `GitHub Commit Bot` is a Python-based tool that automatically makes daily commits to your repository at random times. Plus, it picks one random day each week to push multiple commits instead of just one, giving your commit history a bit more of a random, natural look.

<br/>

## **Features**
- **Daily Commits**: Ensures your repo has at least one commit every single day.
- **Random Times**: Schedules each commit at a randomly generated hour and minute.
- **Weekly Multi-Commit Day**: Selects one day each week (also at random) to push multiple commits (6–24 by default).
- **Robust & Monitored**: Optionally uses AWS SNS to send you an email if something goes wrong.
- **Systemd Integration**: Runs on a Linux server (e.g., AWS EC2 - Ubuntu) as a background service that auto-starts and restarts on crashes.

## **How It Works**
1. A Python script (`commit_bot.py`) uses the schedule library to set up:
   - One commit per day at a random time.
   - Multiple random commits on one random day each week.
2. The script modifies a simple text file (e.g., `commit-log.txt`) and runs `git add`, `git commit`, and `git push`.
3. At the start of each new ISO week, the bot picks a new “multi-commit” day.
4. Systemd ensures the bot keeps running, restarts on failure, and starts automatically on server reboot.

<br/>

## **Prerequisites**
- A small Linux server with Python 3 installed (tested on AWS EC2 t2.micro - Ubuntu 24.04 LTS).
- A cloned GitHub repository on the server (so the bot can commit to it).
- Git installed and configured with either:
  - SSH keys (recommended and tested), or
  - an HTTPS Personal Access Token (PAT).
- (Optional) An AWS SNS topic for failure alert emails.

## **Usage**
1. Clone this repo (or place `commit_bot.py` in an existing repo).
2. Install dependencies (e.g., `schedule`, and `boto3` if you’re using SNS):
   ```
   pip3 install schedule boto3
   ```
3. Configure the script:
   - Edit the `REPO_PATH` to point to your cloned repo folder.
   - Adjust commit frequency settings, and SNS topic ARN, if you want email alerts.
4. Configure email address and name:
   - Run below commands to update email address and name:
     ```
     git config --global user.email "example@domain.com"
     git config --global user.name "Example Name"
     ```
5. Test by running:
   - Run the commit method in python shell:
     ```
     python3
     ```
        ```
        from commit_bot import do_commit_action
        do_commit_action("Test commit")
        ```
     You should see a test commit in your repository.
   - Run the script:
     ```
     python3 commit_bot.py
     ```
     Leave it running; it will make a commit at a random time.
6. Deploy as a service (optional but recommended):
   - Example `Systemd Unit File`
     ```
     [Unit]
     Description=Commit Bot Service
     After=network.target

     [Service]
     Type=simple
     ExecStart=/usr/bin/python3 /home/ubuntu/github-commit-bot/commit_bot.py
     WorkingDirectory=/home/ubuntu/github-commit-bot
     Restart=always
     RestartSec=3600
     User=ubuntu

     [Install]
     WantedBy=multi-user.target
     ```
   - Use `systemd` to manage the script:
     ```
     sudo systemctl daemon-reload
     sudo systemctl enable commitbot.service
     sudo systemctl start commitbot.service
     ```
   - This ensures your bot starts on boot and restarts if it crashes.
7. Check your commits on GitHub! You should see daily commits and one multi-commit day each week.

## **Customization**
- **Time Windows**: If you only want commits between certain hours, modify `random.randint(0, 23)` to a narrower range.
- **Number of Commits**: Change `MIN_COMMITS_RANDOM_DAY` and `MAX_COMMITS_RANDOM_DAY` to schedule more or fewer commits on the multi-commit day.
- **SNS Alerts**: If you don’t want alerts, remove or disable the SNS lines. If you do want them, ensure your IAM role or credentials allow `sns:Publish`.

<br/>

## **Why Use It?**
- `Keep a GitHub streak going` even when you’re too busy to code every day.
- Experiment with scheduling commits for educational or demonstration purposes.
- Practice CI/CD or DevOps workflows in a safe, fun project.

<br/>

## **Disclaimer**
This bot is meant for fun or internal automation. Using it just to artificially inflate commit histories may not reflect real productivity. Use responsibly!

<br/>

## **Contributing**
Feel free to open issues and pull requests if you have ideas or improvements:
- Additional features (e.g., more granular scheduling).
- Advanced logging/monitoring integrations.
- Dockerization or broader OS support.

<br/>

## **License**
This project is released under the `MIT License`. That means you’re free to use, modify, and distribute the code, but you do so at your own risk.

<br/>

## **Support**
For issues or questions, please file an issue in the Issues section of the repository.

<br/>
<br/>

_Thanks for checking out GitHub Commit Bot! Now go automate your commits and let the streaks roll in._
