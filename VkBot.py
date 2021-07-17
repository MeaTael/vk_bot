import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import pandas as pd
from keyboards import main_keyboard, final_keyboard


class VkBot:
    def __init__(self, vk_token, userdata):
        self.vk_token = vk_api.VkApi(token=vk_token)
        self.userdata = pd.read_csv(userdata)
        self.file_userdata = userdata
        self.all_users, self.idtoin, index = set(), dict(), 0
        for user_id in self.userdata.loc[:, 'id']:
            self.all_users.add(user_id)
            self.idtoin[user_id] = index
            index += 1

    def answer_wo_kb(self, user_id, text):
        self.vk_token.method("messages.send", {"user_id": user_id, "message": text, "random_id": 0})

    def answer(self, user_id, text, keyboard):
        self.vk_token.method("messages.send",
                             {"user_id": user_id, "message": text, "random_id": 0, 'keyboard': keyboard})

    def add_user(self, user_id, time):
        if user_id not in self.all_users:
            self.idtoin[user_id] = len(self.idtoin)
            self.all_users.add(user_id)
            new_user = pd.DataFrame([[user_id, 0, 'start', 0, 0, 0]],
                                    columns=['id', 'msg_count', 'user_stage', 'stage game', 'user_page', 'last_time'])
            self.userdata = pd.concat([self.userdata, new_user], ignore_index=True)
            return True
        return False

    def upd_user(self, user_id, time):
        self.userdata.loc[self.idtoin[user_id], 'msg_count'] += 1
        self.userdata.loc[self.idtoin[user_id], 'last_time'] = time

    def antispam(self, user_id, time):
        if time - self.userdata.loc[self.idtoin[user_id], 'last_time'] < 1:
            self.answer_wo_kb(user_id, "Ограничение: не более 1 запроса в 1 секунду")
            return True

    def main_menu(self, user_id):
        self.userdata.loc[self.idtoin[user_id], 'user_stage'] = 'main'
        self.userdata.loc[self.idtoin[user_id], 'stage_game'] = 0
        self.answer(user_id, "Выберите действие", main_keyboard)

    def game_select_page(self, user_id):
        self.userdata.loc[self.idtoin[user_id], 'user_stage'] = 'game_select'
        self.userdata.loc[self.idtoin[user_id], 'stage_game'] = 0
        self.userdata.loc[self.idtoin[user_id], 'user_page'] = 1
        data = pd.read_csv("keyboards.csv")
        keyboard = data[(data.type == 'games') & (data.page == 1)]['code'].iloc[0]
        max_pages = data[(data.type == 'games') & (data.page == 1)]['max_pages'].iloc[0]
        self.answer(user_id, "Выберите игру (страница 1 из " + str(max_pages) + ")", keyboard)

    def next_games_page(self, user_id, next):
        data = pd.read_csv("keyboards.csv")
        max_pages = data[(data.type == 'games') & (data.page == 1)]['max_pages'].iloc[0]
        if next:
            if max_pages > self.userdata.loc[self.idtoin[user_id], 'user_page']:
                self.userdata.loc[self.idtoin[user_id], 'user_page'] += 1
        else:
            if 1 < self.userdata.loc[self.idtoin[user_id], 'user_page']:
                self.userdata.loc[self.idtoin[user_id], 'user_page'] -= 1
        self.userdata.loc[self.idtoin[user_id], 'user_stage'] = 'game_select'
        page = int(self.userdata.loc[self.idtoin[user_id], 'user_page'])
        keyboard = data[(data.type == 'games') & (data.page == page)]['code'].iloc[0]
        self.answer(user_id, "Выберите игру (страница " + str(page) + " из " + str(max_pages) + ")", keyboard)

    def league_select_page(self, user_id, text):
        data = pd.read_csv("keyboards.csv")
        if text not in data[(data.type == 'games') & (data.page == 1)]['games_list'].iloc[0].split('*'):
            self.answer_wo_kb(user_id,
                              "Такой игры нет или же введена неправильная команда. Лучше воспользуйся кнопками")
        elif data[(data.type == 'leagues') & (data.page == 1) & (data.game == text)]['games_list'].iloc[0] == 'empty':
            self.answer_wo_kb(user_id, "К сожалению, турниров по данной игре нет. Попробуй позже")
        else:
            self.userdata.loc[self.idtoin[user_id], 'user_stage'] = 'league_select'
            self.userdata.loc[self.idtoin[user_id], 'stage_game'] = text
            self.userdata.loc[self.idtoin[user_id], 'user_page'] = 1
            keyboard = data[(data.type == 'leagues') & (data.page == 1) & (data.game == text)]['code'].iloc[0]
            max_pages = data[(data.type == 'leagues') & (data.page == 1) & (data.game == text)]['max_pages'].iloc[0]
            self.answer(user_id, "Выберите турнир (страница 1 из " + str(max_pages) + ")", keyboard)

    def next_leagues_page(self, user_id, next):
        data = pd.read_csv("keyboards.csv")
        game = self.userdata.loc[self.idtoin[user_id], 'stage_game']
        max_pages = data[(data.type == 'leagues') & (data.page == 1) & (data.game == game)]['max_pages'].iloc[0]
        if next == 1:
            if max_pages > self.userdata.loc[self.idtoin[user_id], 'user_page']:
                self.userdata.loc[self.idtoin[user_id], 'user_page'] += 1
        elif next == -1:
            if 1 < self.userdata.loc[self.idtoin[user_id], 'user_page']:
                self.userdata.loc[self.idtoin[user_id], 'user_page'] -= 1
        self.userdata.loc[self.idtoin[user_id], 'user_stage'] = 'league_select'
        page = int(self.userdata.loc[self.idtoin[user_id], 'user_page'])
        keyboard = data[(data.type == 'leagues') & (data.page == page) & (data.game == game)]['code'].iloc[0]
        self.answer(user_id, "Выберите турнир (страница " + str(page) + " из " + str(max_pages) + ")", keyboard)

    def show_timetable(self, user_id, text):
        data = pd.read_csv("keyboards.csv")
        data1 = pd.read_csv("GandT_DB.csv")
        if text not in data[
            (data.type == 'leagues') & (data.game == self.userdata.loc[self.idtoin[user_id], 'stage_game'])
        ]['games_list'].iloc[0].split('*'):
            self.answer_wo_kb(user_id,
                              "Такого турнира нет или же введена неправильная команда. Лучше воспользуйся кнопками")
        else:
            self.userdata.loc[self.idtoin[user_id], 'user_stage'] = 'final'
            ans = 'Расписание ' + text + ':\n'
            counter = 1
            for match in data1[(data1.type == 'match') & (data1.league_name == text)]['match_name']:
                ans += str(counter) + ') ' + " vs ".join(match.split('-')) + '\n'
                counter += 1
            self.answer(user_id, ans, final_keyboard)

    def response(self):
        for event in VkLongPoll(self.vk_token).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                user_id, text, time = event.user_id, event.text, event.timestamp
                self.add_user(user_id, time)
                if self.antispam(user_id, time):
                    continue
                self.upd_user(user_id, time)
                user_location = self.userdata.loc[self.idtoin[user_id], 'user_stage']
                if text.lower() == "начать" or text == "Вернуться в основное меню" or text.lower() == "start":
                    self.main_menu(user_id)
                elif text == "Игры" or text == "Вернуться к выбору игры":
                    self.game_select_page(user_id)
                elif text == "Статистика":
                    self.answer_wo_kb(user_id, "Всего пользователей: " + str(len(self.userdata.loc[:, 'id'])) + '\n' +
                                      "Всего запросов: " + str(sum(self.userdata.loc[:, 'msg_count'])) + '\n' +
                                      "Ваших запросов: " + str(self.userdata.loc[self.idtoin[user_id], 'msg_count']))
                elif user_location == 'main' and (text != "Игры" or text != "Статистика"):
                    self.answer_wo_kb(user_id, "Введена неправильная команда. Используй кнопки, пожалуйста")
                elif text == "Следующая страница" and user_location == 'game_select':
                    self.next_games_page(user_id, True)
                elif text == "Предыдущая страница" and user_location == 'game_select':
                    self.next_games_page(user_id, False)
                elif user_location == 'game_select':
                    self.league_select_page(user_id, text)
                elif text == "Следующая страница" and user_location == 'league_select':
                    self.next_leagues_page(user_id, 1)
                elif text == "Предыдущая страница" and user_location == 'league_select':
                    self.next_leagues_page(user_id, -1)
                elif user_location == 'final' and text == 'Вернуться к выбору турнира':
                    self.next_leagues_page(user_id, 0)
                elif user_location == 'final':
                    self.answer(user_id, "Введена неправильная команда. Используй кнопки, пожалуйста", final_keyboard)
                elif user_location == 'league_select':
                    self.show_timetable(user_id, text)

                self.userdata.to_csv(self.file_userdata, encoding='utf-8', index=False)
