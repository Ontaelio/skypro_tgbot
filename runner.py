import requests

from api_utils import user_login, get_board_list, get_categories_list, get_goals_list, get_user_name
from classes import UserStatus
from client import TgClient
from parser import parse_command

from settings import TG_TOKEN, users


def runner(token=TG_TOKEN):
    offset = 0
    tg_client = TgClient(token)
    while True:
        res = tg_client.get_updates(offset=offset, timeout=20)
        for item in res.result:
            offset = item.update_id + 1
            text = item.message.text
            words = text.split()
            user_id = item.message.from_.id
            chat_id = item.message.chat.id
            print(user_id, ':', item.message.text)

            if words[0] == '/login':
                if len(words) != 3:
                    tg_client.send_message(chat_id, 'Please use /login <user> <password>.')
                else:
                    s, name = user_login(words[1], words[2])
                    if s:
                        user_object = UserStatus(username=words[1],
                                                 session=s,
                                                 name=name)
                        users[user_id] = user_object
                        username = user_object.name if user_object.name else user_object.username
                        tg_client.send_message(chat_id, f'Welcome, {username}!')
                    else:
                        tg_client.send_message(chat_id, 'User/password incorrect.')

            else:
                if user := users.get(user_id):
                    if words[0][0] == '/':
                        command, args = parse_command(words)
                        reply = command(user, *args)
                        tg_client.send_message(chat_id, str(reply))
                    else:
                        tg_client.send_message(chat_id, 'Please use commands. /help is helpful.')

            prompt = 'Awaiting your command, Master.' if user_id in users else 'Please login.'

            tg_client.send_message(chat_id, prompt)


if __name__ == '__main__':
    runner()
