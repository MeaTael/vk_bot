import requests
from bs4 import BeautifulSoup
import pandas as pd


def cases(number):
    if 10 <= number % 100 <= 20:
        return " матчей"
    elif number % 10 == 2 or number % 10 == 3 or number % 10 == 4:
        return " матча"
    elif number % 10 == 1:
        return " матч"
    else:
        return " матчей"


def plus_3hrs(date_time):
    date, time = date_time.split()
    hrs, mins = time.split(':')
    hrs = int(hrs)+3
    if hrs//24 == 1:
        hrs %= 24
        day, month = date.split('.')
        day = int(day) + 1
        date = '.'.join([str(day), month])
    time = ':'.join([str(hrs), mins])
    date_time = ' '.join([date, time])
    return date_time


class Parse:
    def __init__(self, link):
        self.html_code = requests.get(link).content
        self.soup = BeautifulSoup(self.html_code, 'html.parser')

    def find_games(self):
        games_set = set()
        res = 'Список всех игр:\n'
        for el in self.soup.find_all('a', 'link'):
            if '.' in el.text.strip():
                games_set.add(el.text.strip().split('.')[0])
        games_set = list(games_set)
        games_set.sort()
        for number in range(len(games_set)):
            res += str(number + 1) + ') ' + games_set[number] + '\n'
        return games_set

    def find_leagues(self):
        leagues_list = list()
        leagues_links_list = list()
        for el in self.soup.find_all('a', 'link'):
            if '.' in el.text.strip():
                leagues_list.append(el.text.strip())
                leagues_links_list.append('https://1xstavka.ru/' + el['href'])
        return leagues_list, leagues_links_list

    def find_matches(self, link):
        html_code = requests.get(link).content
        soup = BeautifulSoup(html_code, 'html.parser')
        matches_list = list()
        find_titles = soup.find_all('span', 'gname')
        find_time = soup.find_all('div', 'c-events__time min')
        for i in range(len(find_titles)-len(find_time)):
            find_time.append(None)
        for number in range(len(find_titles)):
            if find_time[number] is not None:
                matches_list.append(find_titles[number].text + ' | ' + plus_3hrs(find_time[number].text))
            else:
                matches_list.append(find_titles[number].text + ' | ' + "Время пока еще неизвестно")
        print(matches_list)
        return matches_list


def update():
    parser = Parse('https://1xstavka.ru/line/Esports')
    games = parser.find_games()
    leagues, leagues_links = parser.find_leagues()
    leagues_info = dict()
    for number in range(len(leagues)):
        leagues_info[leagues[number]] = leagues_links[number]
    new_data = pd.DataFrame(columns=['type', 'game_name', 'league_name', 'matches_count', 'match_name', 'num'])
    counter = 1
    for game in games:
        new_game = pd.DataFrame([['game', game, 0, 0, 0, counter]],
                                columns=['type', 'game_name', 'league_name', 'matches_count', 'match_name', 'num'])
        new_data = pd.concat([new_data, new_game], ignore_index=True)
        counter += 1
    counter = 0
    prev_game = ''
    leagues.sort()
    for league in leagues:
        if prev_game == league.split('.')[0]:
            counter += 1
        else:
            counter = 1
        prev_game = league.split('.')[0]
        new_league = pd.DataFrame([['league', league.split('.')[0],
                                    ' '.join(' '.join(league.split('.')[1:]).split()[:-1]),
                                    ''.join(' '.join(league.split('.')[1:]).split()[-1]) +
                                    cases(int(''.join(' '.join(league.split('.')[1:]).split()[-1]))), 0, counter]],
                                  columns=['type', 'game_name', 'league_name', 'matches_count', 'match_name', 'num'])
        new_data = pd.concat([new_data, new_league], ignore_index=True)
        matches = parser.find_matches(leagues_info[league])
        for match in matches:
            new_match = pd.DataFrame([['match', league.split('.')[0], ' '.join(' '.join(league.split('.')[1:]).split()[:-1]),
                                       0, match, 0]],
                                     columns=['type', 'game_name', 'league_name', 'matches_count', 'match_name', 'num'])
            new_data = pd.concat([new_data, new_match], ignore_index=True)
    new_data.to_csv('GandT_DB.csv', encoding='utf-8', index=False)

#while True:
   # update()
   # print('READY, sleeping')
  #  t.sleep(600)
