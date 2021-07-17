import json
import pandas as pd


def get_but(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


def get_keyboard(buttons_list):
    keyboard = {
        "one_time": False,
        "buttons": buttons_list
    }
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


main_keyboard = get_keyboard([[get_but('Игры', 'positive')], [get_but('Статистика', 'positive')]])
final_keyboard = get_keyboard([[get_but("Вернуться к выбору игры", 'primary')], [get_but('Вернуться к выбору турнира', 'secondary')], [get_but('Вернуться в основное меню', 'negative')]])


def get_games_keyboard():
    data = pd.read_csv("GandT_DB.csv")
    keyboard_list = list()
    games_list = data[data.type == 'game']['game_name']
    games_list1 = [game_name for game_name in games_list]
    games_count = len(games_list)
    if games_count <= 9:
        but_list = list()
        for game_name in games_list:
            but_list.append([get_but(game_name, 'positive')])
        but_list.append([get_but("Вернуться в основное меню", 'negative')])
        keyboard_list.append(get_keyboard(but_list))
    else:
        but_list = list()
        for game_number in range(8):
            but_list.append([get_but(games_list.iloc[game_number], 'positive')])
        but_list.append([get_but("Следующая страница", 'primary')])
        but_list.append([get_but("Вернуться в основное меню", 'negative')])
        keyboard_list.append(get_keyboard(but_list))
        for page_number in range((games_count-8)//7+((games_count-8) % 7 != 0)):
            but_list = list()
            but_list.append([get_but("Предыдущая страница", 'primary')])
            for game_number in range(7):
                if 8 + page_number * 7 + game_number >= games_count:
                    continue
                but_list.append([get_but(games_list.iloc[8 + page_number * 7 + game_number], 'positive')])
            if page_number+1 != (games_count-8)//7+((games_count-8) % 7 != 0):
                but_list.append([get_but("Следующая страница", 'primary')])
            but_list.append([get_but("Вернуться в основное меню", 'negative')])
            keyboard_list.append(get_keyboard(but_list))
    return keyboard_list, games_list1


def get_leagues_keyboard(games_list):
    data = pd.read_csv("GandT_DB.csv")
    games_dict = dict()
    games_dict_ls = dict()
    for game_name in games_list:
        keyboard_list = list()
        leagues_list1 = data[(data.type == 'league') & (data.game_name == game_name)]['league_name']
        leagues_list = list()
        for league in leagues_list1:
            if len(league) <= 40:
                leagues_list.append(league)
        leagues_count = len(leagues_list)
        if leagues_count <= 8:
            but_list = list()
            for league_name in leagues_list:
                but_list.append([get_but(league_name, 'positive')])
            but_list.append([get_but("Вернуться к выбору игры", 'secondary')])
            but_list.append([get_but("Вернуться в основное меню", 'negative')])
            keyboard_list.append(get_keyboard(but_list))
        else:
            but_list = list()
            for league_number in range(7):
                league_name = leagues_list[league_number]
                but_list.append([get_but(league_name, 'positive')])
            but_list.append([get_but("Следующая страница", 'primary')])
            but_list.append([get_but("Вернуться к выбору игры", 'secondary')])
            but_list.append([get_but("Вернуться в основное меню", 'negative')])
            keyboard_list.append(get_keyboard(but_list))
            for page_number in range((leagues_count - 7) // 6 + ((leagues_count - 7) % 6 != 0)):
                but_list = list()
                but_list.append([get_but("Предыдущая страница", 'primary')])
                for league_number in range(6):
                    if 7 + page_number * 6 + league_number >= leagues_count:
                        continue
                    league_name = leagues_list[7 + page_number * 6 + league_number]
                    but_list.append([get_but(league_name, 'positive')])
                if page_number + 1 != (leagues_count - 7) // 6 + ((leagues_count - 7) % 6 != 0):
                    but_list.append([get_but("Следующая страница", 'primary')])
                but_list.append([get_but("Вернуться к выбору игры", 'secondary')])
                but_list.append([get_but("Вернуться в основное меню", 'negative')])
                keyboard_list.append(get_keyboard(but_list))
        games_dict[game_name] = keyboard_list
        games_dict_ls[game_name] = '*'.join(leagues_list)
    return games_dict, games_dict_ls



def update_keyboards():
    new_keyboard_base = pd.DataFrame(columns=['type', 'game', 'page', 'max_pages', 'code', 'games_list'])
    page_counter = 1
    keyboard_list, games_list = get_games_keyboard()
    for keyboard in keyboard_list:
        new_keyboard = pd.DataFrame([['games', 0, page_counter, len(keyboard_list), keyboard, '*'.join(games_list)]], columns=['type', 'game', 'page', 'max_pages', 'code', 'games_list'])
        new_keyboard_base = pd.concat([new_keyboard_base, new_keyboard], ignore_index=True)
        page_counter += 1
    keyboard_dict, leagues_dict = get_leagues_keyboard(games_list)
    for key in keyboard_dict.keys():
        page_counter = 1
        keyboard_list = keyboard_dict[key]
        leagues_list = leagues_dict[key]
        if leagues_list == '':
            leagues_list = 'empty'
        for keyboard in keyboard_list:
            new_keyboard = pd.DataFrame([['leagues', key, page_counter, len(keyboard_list), keyboard, leagues_list]], columns=['type', 'game', 'page', 'max_pages', 'code', 'games_list'])
            new_keyboard_base = pd.concat([new_keyboard_base, new_keyboard], ignore_index=True)
            page_counter += 1
    new_keyboard_base.to_csv("keyboards.csv", encoding='utf-8', index=False)
