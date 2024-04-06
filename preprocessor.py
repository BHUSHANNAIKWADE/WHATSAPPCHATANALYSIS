import re
import pandas as pd

def preprocess(data):
    pattern = r'\[\d{2}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\] '

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'date': dates, 'message': messages})
    df['date'] = pd.to_datetime(df['date'].str.extract(r'\[(.*?)\]')[0], format='%d/%m/%y, %H:%M:%S')

    users = []
    messages = []
    links = []  # New column for links
    for message in df['message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            message_text = " ".join(entry[2:])
            messages.append(message_text)
            extracted_links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)
            links.append(", ".join(extracted_links))
        else:
            users.append('group_notification')
            messages.append(entry[0])
            links.append("")

    df['user'] = users
    df['message'] = messages
    df['links'] = links  # Add links column
    df['only_date'] = df['date'].dt.date

    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
