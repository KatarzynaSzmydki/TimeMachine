import requests
from bs4 import BeautifulSoup

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:")
URL = 'https://www.billboard.com/charts/hot-100/' + date

request = requests.get(URL)
soup = BeautifulSoup(request.text, 'html.parser')
soup.select('pmc-paywall')
title = soup.select("li #title-of-a-story")
titles = [song_title.getText().strip() for song_title in title]


