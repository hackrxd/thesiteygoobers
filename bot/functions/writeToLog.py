import datetime

def log(logMessage):
    with open(f'bot/logs/log-{datetime.date.today()}.log', 'a') as log_file:
        log_file.write(f'[{datetime.datetime.now()}] {logMessage}\n')