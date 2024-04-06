import helper
import streamlit as st
import base64
from preprocessor import preprocess

import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import seaborn as sns
import numpy as np



# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "get_started"


def main():
    if st.session_state.page == "get_started":
        get_started_page()
    elif st.session_state.page == "analysis":
        analysis_page()


def get_started_page():
    st.title("Welcome to WhatsApp Chat Analyzer!")

    st.write("This app helps analyze your WhatsApp chat data.")
    st.write("WhatsApp Chat Analyzer allows you to gain insights into your WhatsApp conversations. "
             "Upload your chat data, and it will provide you with various analyses, including message statistics, "
             "interesting views, activity maps, and more.")

    # Set background color
    st.markdown(
        """
        <style>
        body {
            background-color: #007f73;
        }
        </style>
        """,
        unsafe_allow_html=True
    )



    # Example data for pie chart
    labels_pie = ['A', 'B', 'C', 'D']
    sizes_pie = [15, 30, 45, 10]
    explode_pie = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'B')
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes_pie, explode=explode_pie, labels=labels_pie, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Example data for bar graph
    labels_bar = ['A', 'B', 'C', 'D']
    values1_bar = [10, 20, 30, 40]
    values2_bar = [5, 25, 35, 45]
    x_bar = np.arange(len(labels_bar))
    width_bar = 0.35  # the width of the bars
    fig2, ax2 = plt.subplots()
    rects1 = ax2.bar(x_bar - width_bar / 2, values1_bar, width_bar, label='Group 1')
    rects2 = ax2.bar(x_bar + width_bar / 2, values2_bar, width_bar, label='Group 2')
    ax2.set_xticks(x_bar)
    ax2.set_xticklabels(labels_bar)
    ax2.legend()

    # Create columns to display the graphs side by side
    col1, col2 = st.columns(2)

    with col1:
        st.pyplot(fig1)

    with col2:
        st.pyplot(fig2)

# Display steps for exporting chats on Android and iOS below the graphs
    st.markdown("## Exporting Chats Instructions")
    with st.expander("Android"):
        st.write("**Android:**")
        st.write("1. Open WhatsApp and go to the chat you want to export.")
        st.write("2. Tap on the three dots at the top right corner.")
        st.write("3. Select 'More' > 'Export chat'.")
        st.write("4. Choose whether to include media files or not.")
        st.write("5. Select the app or method through which you want to share the exported chat.")

    with st.expander("iOS (iPhone)"):
        st.write("**iOS (iPhone):**")
        st.write("1. Open WhatsApp and navigate to the chat you want to export.")
        st.write("2. Tap on the contact or group name at the top of the chat.")
        st.write("3. Scroll down and tap 'Export Chat'.")
        st.write("4. Choose whether to export 'Without Media' or 'Attach Media'.")
        st.write("5. Select the app or method through which you want to share the exported chat.")



    # Create an empty slot at the bottom
    bottom_slot = st.empty()
    with bottom_slot:
        if st.button("Get Started"):
            st.session_state.page = "analysis"


@st.cache
def preprocess_data(data, db_path):
    processed_data = preprocess(data)
    return processed_data


def analysis_page():
    st.sidebar.title("WhatsApp Chat Analyzer")

    uploaded_file = st.sidebar.file_uploader("Choose a file")

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        db_path = 'whatsapp_analysis.db'
        df = preprocess_data(data, db_path)

        # fetch unique users
        user_list = df['user'].unique().tolist()
        user_list.sort()
        user_list.insert(0, "Overall")

        # Create a sidebar selectbox for user selection
        selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

        # Fetch statistics for the selected user
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"**Total Messages:** {num_messages}")
        with col2:
            st.markdown(f"**Total Words:** {words}")
        with col3:
            st.markdown(f"**Media Shared:** {num_media_messages}")
        with col4:
            st.markdown(f"**Links Shared:** {num_links}")

        if selected_user != "Overall":
            user_specific_analysis(selected_user, df)  # Add this line to call the function for single user analysis


    # Additional Analysis: Busy Users (Pie Chart)
        st.title("Most Busy Users (Pie Chart)")
        x, new_df = helper.most_busy_users(df)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(x.values, labels=x.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)
        st.dataframe(new_df)

        # Add a sidebar dropdown menu to select another user for comparison
        comparison_user = st.sidebar.selectbox("Compare with", user_list)

        if comparison_user != selected_user and comparison_user != "Overall":
            compare_users(selected_user, comparison_user, df)


def compare_users(user1, user2, df):
    # Fetch statistics for both users
    stats_user1 = helper.fetch_stats(user1, df)
    stats_user2 = helper.fetch_stats(user2, df)

    # Calculate number of links shared for each user
    num_links_user1 = stats_user1[3]
    num_links_user2 = stats_user2[3]

    # Create a DataFrame for comparison
    comparison_df = pd.DataFrame({
        "User": [user1, user2],
        "Total Messages": [stats_user1[0], stats_user2[0]],
        "Total Words": [stats_user1[1], stats_user2[1]],
        "Media Shared": [stats_user1[2], stats_user2[2]],
        "Links Shared": [num_links_user1, num_links_user2]  # Add links shared column
    })

    # Plotting comparison in a bar graph
    st.title("Comparison of User Analysis")
    fig = px.bar(comparison_df, x="User", y=["Total Messages", "Total Words", "Media Shared", "Links Shared"],
                 barmode='group', title="Comparison of User Analysis")
    st.plotly_chart(fig)

    # Display daily timeline for each user in bar graph format
    st.title("Daily Timeline Comparison")
    daily_timeline_user1 = helper.daily_timeline(user1, df)
    daily_timeline_user2 = helper.daily_timeline(user2, df)

    # Plot daily timeline for user 1
    st.subheader(f"Daily Timeline for {user1}")
    fig_user1 = px.bar(daily_timeline_user1, x='only_date', y='message', title=f'Daily Timeline for {user1}')
    st.plotly_chart(fig_user1)

    # Plot daily timeline for user 2
    st.subheader(f"Daily Timeline for {user2}")
    fig_user2 = px.bar(daily_timeline_user2, x='only_date', y='message', title=f'Daily Timeline for {user2}')
    st.plotly_chart(fig_user2)






def user_specific_analysis(selected_user, df):
    st.title(f"Analysis for {selected_user}")

    # Filter data for the selected user
    user_df = df[df['user'] == selected_user]

    # Add first and last message with date
    first_message_date = user_df['date'].min().strftime('%Y-%m-%d %H:%M:%S')
    last_message_date = user_df['date'].max().strftime('%Y-%m-%d %H:%M:%S')

    st.write(f"First message date: {first_message_date}")
    st.write(f"Last message date: {last_message_date}")

    # Additional analysis for week and month activity map
    st.title(f"Weekly Activity Map for {selected_user}")
    busy_week = helper.week_activity_map(selected_user, df)
    days_order = ['Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday', 'Sunday']
    busy_week = busy_week.reindex(days_order)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(busy_week.index, busy_week.values, color='purple')
    ax.set_xlabel('Number of Messages')
    ax.set_ylabel('Day of Week')
    ax.set_title(f"Weekly Activity Map for {selected_user}")
    st.pyplot(fig)

    # Additional Analysis: Media Analysis
    media_data = helper.media_analysis(selected_user, df)
    st.title(f"Media Analysis for {selected_user}")
    media_data.set_index('Media Type', inplace=True)
    st.bar_chart(media_data)

    # Additional Analysis: Message Length Analysis
    message_length_data = helper.message_length_analysis(selected_user, df)
    st.title(f"Message Length Analysis for {selected_user}")
    st.dataframe(message_length_data)

    # Additional Analysis: Word Cloud
    wordcloud_data = helper.create_wordcloud(selected_user, df)
    st.title(f"Word Cloud for {selected_user}")
    st.image(wordcloud_data.to_array(), use_column_width=True)

    # Additional Analysis: Most Common Words
    most_common_words_data = helper.most_common_words(selected_user, df)
    st.title(f"Most Common Words for {selected_user}")
    st.table(most_common_words_data)

    # Additional Analysis: Daily Timeline
    daily_timeline_data = helper.daily_timeline(selected_user, df)
    st.title(f"Daily Timeline for {selected_user}")
    st.line_chart(daily_timeline_data.set_index('only_date'))

    # Additional Analysis: Activity Heatmap
    activity_heatmap_data = helper.activity_heatmap(selected_user, df)
    st.title(f"Activity Heatmap for {selected_user}")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(activity_heatmap_data, cmap="Blues", cbar=True, ax=ax)
    st.pyplot(fig)

    # Additional Analysis: Link Analysis
    unique_links_count, top_domains, link_activity_over_time = helper.link_analysis(df)
    st.title("Link Analysis")
    st.write(f"Unique Links Count: {unique_links_count}")
    st.write("Top Shared Domains:")
    st.table(top_domains)

    # Bar chart for link activity over time
    st.write("Link Activity Over Time:")
    fig = px.bar(link_activity_over_time, x='Date', y='Link_Activity', title='Link Activity Over Time')
    st.plotly_chart(fig)

    # Additional Analysis: Popular Content Analysis
    top_content = helper.popular_content_analysis(df)
    st.title("Popular Content Analysis")
    st.table(top_content)




if __name__ == "__main__":
    main()
