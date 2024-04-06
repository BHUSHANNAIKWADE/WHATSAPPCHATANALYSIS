import pandas as pd
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import emoji
import urlextract
import re
from urllib.parse import urlparse


extract = urlextract.URLExtract()

def fetch_stats(selected_user, df):
    """
    Fetch statistics related to the WhatsApp chat data.

    Parameters:
        selected_user (str): The user for which statistics are fetched.
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        tuple: A tuple containing the following statistics:
            - num_messages (int): The total number of messages sent by the selected user.
            - words (int): The total number of words in the messages sent by the selected user.
            - num_media_messages (int): The total number of media messages (images, videos, etc.) sent by the selected user.
            - num_links (int): The total number of links shared by the selected user.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = sum(df['message'].str.split().apply(len))
    num_media_messages = df[df['message'].str.contains('image omitted')].shape[0]

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, words, num_media_messages, len(links)

def most_busy_users(df):
    """
    Identify the most active users in the WhatsApp chat.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        tuple: A tuple containing the following information:
            - x (pandas.Series): Series with the counts of messages sent by each user.
            - df_percent (pandas.DataFrame): DataFrame with the percentage of messages sent by each user.
    """
    x = df['user'].value_counts().head()
    df_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df_percent

def create_wordcloud(selected_user, df):
    """
    Create a word cloud from the messages of the selected user.

    Parameters:
        selected_user (str): The user for which the word cloud is generated.
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        wordcloud.WordCloud: Word cloud object representing the word frequencies in the messages.
    """
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]

    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    """
    Identify the most common words used by the selected user.

    Parameters:
        selected_user (str): The user for which common words are identified.
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        pandas.DataFrame: DataFrame containing the most common words and their counts.
    """
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[(df['user'] != 'group_notification') & (df['message'] != 'image omitted')]

    words = [word for message in temp['message'] for word in message.lower().split() if word not in stop_words]
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    most_common_df.columns = ['Word', 'Count']  # Add column names for clarity
    return most_common_df

def daily_timeline(selected_user, df):
    """
    Generate a daily timeline of message counts for the selected user.

    Parameters:
        selected_user (str): The user for which the daily timeline is generated.
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        pandas.DataFrame: DataFrame containing the daily message counts.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user, df):
    """
    Generate a weekly activity map for the selected user.

    Parameters:
        selected_user (str): The user for which the weekly activity map is generated.
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        pandas.Series: Series containing the number of messages for each day of the week.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.groupby('day_name').count()['message'].reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0)

def activity_heatmap(selected_user, df):
    """
    Generate an activity heatmap for the selected user.

    Parameters:
        selected_user (str): The user for which the activity heatmap is generated.
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        pandas.DataFrame: DataFrame representing the activity heatmap.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap

def media_analysis(selected_user, df):
    """
    Perform media analysis for the selected user.

    Parameters:
        selected_user (str): The user for which media analysis is performed.
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        pandas.DataFrame: DataFrame containing the count of different types of media shared by the user.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    media_messages = df[df['message'].str.contains('image omitted') | df['message'].str.contains('video omitted') | df[
        'message'].str.contains('document omitted') | df['message'].str.contains('audio omitted')]

    return pd.DataFrame({'Media Type': ['Images', 'Videos', 'Documents', 'Audio'],
                         'Count': [media_messages[media_messages['message'].str.contains('image omitted')].shape[0],
                                   media_messages[media_messages['message'].str.contains('video omitted')].shape[0],
                                   media_messages[media_messages['message'].str.contains('document omitted')].shape[0],
                                   media_messages[media_messages['message'].str.contains('audio omitted')].shape[0]]})

def message_length_analysis(selected_user, df):
    """
    Analyze the message length for the selected user.

    Parameters:
        selected_user (str): The user for which message length analysis is performed.
        df (pandas.DataFrame): The DataFrame containing the WhatsApp chat data.

    Returns:
        pandas.DataFrame: DataFrame containing descriptive statistics of message lengths.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df['message_length'] = df['message'].apply(len)

    return df.groupby('user')['message_length'].describe()

def link_analysis(df):
    # Extract links from messages
    links = []
    for message in df['message']:
        links.extend(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message))

    # Unique links count
    unique_links_count = len(set(links))

    # Top shared domains
    domains = [urlparse(url).netloc if urlparse(url).netloc else 'N/A' for url in links]
    top_domains = pd.DataFrame(Counter(domains).most_common(10), columns=['Domain', 'Count'])

    # Link activity over time
    link_activity_over_time = df.groupby('only_date').size().reset_index(name='Link_Activity')
    link_activity_over_time.columns = ['Date', 'Link_Activity']  # Set the correct column names

    return unique_links_count, top_domains, link_activity_over_time
    pass


def popular_content_analysis(df):
    # Extract content from shared links
    content = []
    for message in df['message']:
        links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        for link in links:
            content.append(link)

    # Calculate content frequency
    content_frequency = Counter(content)

    # Find top shared content
    top_content = pd.DataFrame(content_frequency.most_common(10), columns=['Content', 'Count'])

    return top_content
