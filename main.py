import time
import pandas as pd
from VkBot import VkBot
from keyboards import update_keyboards
from Parser import update


def vk_bot():
    TryBot = VkBot("b4bd8de8b0effae25d78830090b23c2e92d2b195707eaef09ee76daefae5ee2d4e9c91757ee7e8fde5c01", "userbase.csv")
    TryBot.response()


def auto_update():
    while True:
        print('Updating bd')
        try:
            #update()
            data = pd.read_csv("updater.csv")
            data.iloc[0]['updated'] = 1
            data.to_csv("updater.csv", encoding='utf-8', index=False)
            print('updated, sleeping')
            time.sleep(3600)
        except Exception:
            print("smth went wrong, retrying in 10 min")
            time.sleep(600)

def keyboards_update():
    while True:
        time.sleep(10)
        data = pd.read_csv("updater.csv")
        if data.iloc[0]['updated'] == 1:
            data.iloc[0]['updated'] = 0
            data.to_csv("updater.csv", encoding='utf-8', index=False)
            update_keyboards()
            print("Keyboards updated")

from multiprocessing import Process

if __name__ == '__main__':
    Process(target=auto_update).start()
    Process(target=keyboards_update).start()
    Process(target=vk_bot).start()
