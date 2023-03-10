import random
import string

import requests

from classes import UserStatus, GoalItem
from settings import API_URL, users

prohibited_letters = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']


def unknown_command(*args):
    return 'Unknown command, check /help\\.'


def markdowned(text: str) -> str:
    a = []
    for letter in text:
        if letter in prohibited_letters:
            a.append('\\' + letter)
        else:
            a.append(letter)
    return ''.join(a)


def create_code(tg_user):
    letters = string.ascii_lowercase + string.digits
    code = str(''.join(random.choice(letters) for _ in range(8)))

    reply = requests.post(API_URL + f'/bot/connect', data={"tg_user": tg_user, "verification_code": code})

    if reply.status_code not in [200, 201]:
        return f'Not able to bind, error {reply.status_code}\\.'

    return markdowned(f"Enter this code in the web app (\"Verify bot\"):"
                      f" {code}\n"
                      f"Then /verify here.")


def get_board_role(s: UserStatus, num: int):
    reply = s.session.get(API_URL + f'/goals/board/{num}')
    contents = reply.json()
    for p in contents['participants']:
        if p['user'] == s.username:
            return p['role']
    return None


def filter_boards_by_user(boards: list, username: str) -> list:
    reply = []
    for board in boards:
        for p in board['participants']:
            if all([p['user'] == username, p['role'] == 1]):
                reply.append(board)
    return reply


def get_category_board(s: UserStatus):
    reply = s.session.get(API_URL + f'/goals/goal_category/{s.category.id}')
    contents = reply.json()
    return contents['board']


def get_category_details(s: UserStatus):
    reply = s.session.get(API_URL + f'/goals/goal_category/{s.category.id}')
    contents = reply.json()
    return contents['title'], contents['board']


def find_board_local_id(s: UserStatus, num: int):
    for k, b in s.present_boards.items():
        if b.id == num:
            return k
    return None


def find_cat_local_id(s: UserStatus, num: int):
    for k, b in s.present_cats.items():
        if b.id == num:
            return k
    return None


def get_user_name(s: UserStatus, *args):
    reply = s.session.get(API_URL + '/core/profile')
    name = reply.json().get('first_name', None)
    return name


def get_goal_details(s: UserStatus, goal_id) -> GoalItem | None:
    reply = s.session.get(API_URL + f'/goals/goal/{goal_id}')
    goal = GoalItem(**reply.json())
    return goal
