import datetime

def log(logMessage):
    with open(f'logs/log-{datetime.date.today()}.log', 'a') as log_file:
        log_file.write(f'{logMessage}\n')