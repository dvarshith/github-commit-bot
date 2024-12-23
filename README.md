# **GitHub Commit Bot**
Ever wished you had a neat little bot to keep your GitHub streak alive—or just to have some fun with automated commits? GitHub Commit Bot is a Python-based tool that automatically makes daily commits to your repository at random times. Plus, it picks one random day each week to push multiple commits instead of just one, giving your commit history a bit more of a random, natural look.

## **Features**
- **Daily Commits**: Ensures your repo has at least one commit every single day.
- **Random Times**: Schedules each commit at a randomly generated hour and minute.
- **Weekly Multi-Commit Day**: Selects one day each week (also at random) to push multiple commits (2–5 by default).
- **Robust & Monitored**: Optionally uses AWS SNS to send you an email if something goes wrong.
- **Systemd Integration**: Runs on a Linux server (e.g., Ubuntu/Amazon Linux 2) as a background service that auto-starts and restarts on crashes.

## **How It Works**
1. A Python script (commit_bot.py) uses the schedule library to set up:
   - One commit per day at a random time.
   - Multiple random commits on one random day each week.
2. The script modifies a simple text file (e.g., auto_commit.txt) and runs git add, git commit, and git push.
3. At the start of each new ISO week, the bot picks a new “multi-commit” day.
4. Systemd ensures the bot keeps running, restarts on failure, and starts automatically on reboot.

## **Prerequisites**
- A Linux environment with Python 3 installed (tested on Ubuntu, Amazon Linux 2, etc.).
- A cloned GitHub repository on the server (so the bot can commit to it).
- Git installed and configured with either:
  - SSH keys (recommended), or
  - an HTTPS Personal Access Token (PAT).
- (Optional) An AWS SNS topic for failure alert emails.

## **Usage**
1. Clone this repo (or place commit_bot.py in an existing repo).
2. Install dependencies (e.g., schedule and boto3 if you’re using SNS):
   ```
   pip3 install schedule boto3
   ```
3. Configure the script:
   - Edit the REPO_PATH to point to your cloned repo folder.
   - Adjust commit frequency settings, SNS topic ARN, etc. if you want email alerts.
4. Test by running:
   ```
   python3 commit_bot.py
   ```
   Leave it running; it will make a commit at a random time.
5. Deploy as a service (optional but recommended):
   - Use systemd to manage the script:
     ```
     sudo systemctl daemon-reload
     sudo systemctl enable commitbot.service
     sudo systemctl start commitbot.service
     ```
   - This ensures your bot starts on boot and restarts if it crashes.
6. Check your commits on GitHub! You should see daily commits and one multi-commit day each week.
   Example Systemd Unit File
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

## **Customization**
- **Time Windows**: If you only want commits between certain hours, modify random.randint(0, 23) to a narrower range.
- **Number of Commits**: Change MIN_COMMITS_RANDOM_DAY and MAX_COMMITS_RANDOM_DAY to schedule more or fewer commits on the multi-commit day.
- **SNS Alerts**: If you don’t want alerts, remove or disable the SNS lines. If you do want them, ensure your IAM role or credentials allow sns:Publish.

## **Why Use It?**
- Keep a GitHub streak going even when you’re too busy to code every day.
- Experiment with scheduling commits for educational or demonstration purposes.
- Practice CI/CD or DevOps workflows in a safe, fun project.

## **Disclaimer**
This bot is meant for fun or internal automation. Using it just to artificially inflate commit histories may not reflect real productivity. Use responsibly!

## **Contributing**
Feel free to open issues and pull requests if you have ideas or improvements:
- Additional features (e.g., more granular scheduling).
- Advanced logging/monitoring integrations.
- Dockerization or broader OS support.

## **License**
This project is released under the MIT License. That means you’re free to use, modify, and distribute the code, but you do so at your own risk.

## **Support**
For issues or questions, please file an issue in the Issues section of the repository.

Thanks for checking out GitHub Commit Bot! Now go automate your commits and let the streaks roll in.
