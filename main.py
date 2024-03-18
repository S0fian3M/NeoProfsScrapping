import random
import re
import csv
import time

import requests
from bs4 import BeautifulSoup

csv_file = "dataset.csv"

# URL of the website you want to scrape
neo_profs_url = 'https://www.neoprofs.org/'
neo_profs_forum_url = neo_profs_url + 'forum'

# Send a GET request to the main URL
response = requests.get(neo_profs_forum_url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page
    soup_global = BeautifulSoup(response.text, 'html.parser')

    # Extract all forum titles
    a_forum_titles = soup_global.find_all('a', class_='forumtitle')

    # Open the CSV file (we will write all data inside it)
    with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        # Instantiate a CSV Writer
        fieldnames = ['username', 'rank', 'date', 'content', 'topic_id', 'forum_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Loop through all forums
        for a_forum_title in a_forum_titles:
            match_forum_titles = re.match(r'^\/(\w*)([a-zA-Z0-9_\-]*)', a_forum_title.get('href'))

            if match_forum_titles:
                # Get id and title from the match element
                forum_id_url = match_forum_titles.group(1)
                forum_title_url = match_forum_titles.group(2)
                # Concatenate to create the forum URL
                forum_url = f"{neo_profs_url}{forum_id_url}{forum_title_url}"
                nb_topic_per_forum = 0

                while True:
                    # Send a GET request to the forum URL
                    time.sleep(random.randint(30, 90))
                    print(forum_url)
                    response = requests.get(forum_url)

                    if response.status_code == 200:
                        # Parse the HTML content of the page
                        soup_forum = BeautifulSoup(response.text, 'html.parser')

                        # Extract all topic titles
                        a_topic_titles = soup_forum.select('div.forumbg:not(.announcement) a.topictitle') if nb_topic_per_forum == 0 else soup_forum.select('a.topictitle')
                        if a_topic_titles is None or len(a_topic_titles) == 0:
                            break

                        # Loop through all topics
                        for a_topic_title in a_topic_titles:
                            # Match the link with a regex
                            match_topic_titles = re.match(r'^\/(\w*)([a-zA-Z0-9_\-]*)', a_topic_title.get('href'))

                            if match_topic_titles:
                                # Get id and title from the match element
                                topic_id_url = match_topic_titles.group(1)
                                topic_title_url = match_topic_titles.group(2)
                                # Concatenate to create the topic URL
                                topic_url = f"{neo_profs_url}{topic_id_url}{topic_title_url}"
                                nb_messages_per_topic = 0

                                while True:
                                    # Send a GET request to the topic URL
                                    time.sleep(random.random())
                                    print(f"      {topic_url}")
                                    response = requests.get(topic_url)

                                    if response.status_code == 200:
                                        # Parse the HTML content of the page
                                        soup = BeautifulSoup(response.text, 'html.parser')

                                        # Extract all posts
                                        post_divs = soup.find_all('div', class_='post')
                                        if post_divs is None or len(post_divs) == 0:
                                            break

                                        # Print the content of each selected div
                                        all_data = []
                                        for post_div in post_divs:
                                            # Extract data from raw posts
                                            postprofile_name = post_div.find('div', class_='postprofile-name').text
                                            postprofile_rank = post_div.find('div', class_='postprofile-rank').text
                                            content = post_div.find('div', class_='content')
                                            # Date
                                            author_date = post_div.find('div', class_='author')
                                            full_date = re.search(re.compile(r'(Lun|Mar|Mer|Jeu|Ven|Sam|Dim)(.*)'), author_date.text)
                                            # full_date = re.match(
                                            #     r"par [a-zA-Z0-9_\-\.\*@àáâãäåæéèêëìíîïñòóôöõøœçùúûüýÿÆÂÀÄÂÃÇÉÈÊËÎÏÔÖÕÛÜÙÚ]* (.*)",
                                            #     ' '.join([text.strip() for text in author_date.find_all(text=True)
                                            #               if not isinstance(text.find_parent('a'), type(author_date))])
                                            # )
                                            author_date = full_date.group(0) if full_date else None

                                            # Remove blockquotes (repeating a previous post as an answer)
                                            text_content = ' '.join([text.strip() for text in content.find_all(text=True) if
                                                                     not isinstance(text.find_parent('blockquote'), type(content))])
                                            all_data.append(
                                                {
                                                    "username": postprofile_name,
                                                    "rank": postprofile_rank,
                                                    "date": author_date,
                                                    "content": text_content,
                                                    "topic_id": topic_id_url,
                                                    "forum_id": forum_id_url
                                                }
                                            )

                                        # Write topic data inside the CSV file
                                        writer.writerows(all_data)
                                    else:
                                        print(f"Failed to retrieve the page: {topic_url}. Status code: {response.status_code}")
                                        break

                                    # Go to the next topic URL
                                    nb_messages_per_topic += 25
                                    topic_url = f"{neo_profs_url}{topic_id_url}p{nb_messages_per_topic}{topic_title_url}"
                    else:
                        print(f"Failed to retrieve the page: {forum_url}. Status code: {response.status_code}")
                        break

                    # Go to the next forum URL
                    nb_topic_per_forum += 50
                    forum_url = f"{neo_profs_url}{forum_id_url}p{nb_topic_per_forum}{forum_title_url}"
