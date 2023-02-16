import logging

import requests

from api_handlers.api_views import user_login, get_board_list, check_binding
from api_handlers.utils import markdowned, create_code
from classes import UserStatus
from client import TgClient
from api_handlers.parser import parse_command, split_double_quoted
from exceptions import CommandUnavailable

from settings import TG_TOKEN, users


def runner(token=TG_TOKEN):
    offset = 0
    tg_client = TgClient(token)
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT)

    while True:
        res = tg_client.get_updates(offset=offset, timeout=60)
        if not res:
            continue
        for item in res.result:
            offset = item.update_id + 1
            text = item.message.text
            words = split_double_quoted(text)
            user_id = item.message.from_.id
            chat_id = item.message.chat.id
            first_name = item.message.from_.first_name
            logging.warning(f'User {user_id} from chat {chat_id}: {item.message}')

            # check if user is bound
            if user_id not in users:
                users[user_id] = UserStatus(session=requests.Session())
                users[user_id].session.headers.update({'tg-user': str(user_id)})
                base_id, username, name = check_binding(users[user_id])
                if base_id:
                    users[user_id].id = base_id
                    users[user_id].username = username
                    users[user_id].name = name if name else first_name
                    users[user_id].tg_user = user_id
                    tg_client.send_message(chat_id,
                                           f'Welcome, {markdowned(users[user_id].name)}\\!\n'
                                           + get_board_list(users[user_id]))
                else:
                    del users[user_id]

            # commands that are available without login
            if words[0].lower() == '/bind':
                tg_client.send_message(chat_id, create_code(user_id))

            elif words[0].lower() == '/login':
                if len(words) == 3:
                    s, name, base_id = user_login(words[1], words[2])
                    if s:
                        name = first_name if not name else name
                        user_object = UserStatus(username=words[1],
                                                 session=s,
                                                 name=name,
                                                 id=base_id,
                                                 tg_user=user_id)
                        if not user_object.name: user_object.name = user_object.username
                        users[user_id] = user_object
                        tg_client.send_message(chat_id,
                                               f'Welcome, {markdowned(user_object.name)}\\!\n' + get_board_list(
                                                   user_object))
                    else:
                        tg_client.send_message(chat_id, 'User/password incorrect\\.')

            # and now for actual commands
            else:
                if user := users.get(user_id):
                    if words[0].isdecimal():
                        words = [user.default_command, words[0]]
                    if words[0].startswith('/'):  # [0] == '/':
                        command, args = parse_command(words)
                        try:
                            reply = command(user, *args)
                        except CommandUnavailable as e:
                            reply = markdowned(str(e))

                        try:
                            tg_client.send_message(chat_id, str(reply))
                        except:  # this is most certainly a markdown TG bot error, I need to catch it to know the name
                            tg_client.send_message(chat_id, 'Something really weird happened, most likely with evil '
                                                            'characters used\\.')
                    else:
                        tg_client.send_message(chat_id, 'Please use commands\\. /help is helpful\\.')

            prompt = 'Awaiting your command, Master\\.' if user_id in users \
                else 'Please `/login \\<user\\> \\<password\\>` or `/bind` your account\\.'

            tg_client.send_message(chat_id, prompt)


if __name__ == '__main__':
    runner()
