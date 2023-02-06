import requests

from classes import UserStatus, PresentItem
from settings import API_URL

prohibited_letters = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
role_string = {
    1: 'You *own* this place\\!',
    2: 'You can *write and edit* here\\.',
    3: 'You are a *reader* here\\.'
}


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


def user_login(username, password):
    s = requests.Session()
    s.auth = (username, password)
    reply = s.get(API_URL + '/core/profile')
    if reply.status_code == 200:
        name = reply.json().get('first_name', None)
        user_id = reply.json().get('id')
        return s, name, user_id
    return None, None, None


def get_user_name(s: UserStatus, *args):
    reply = s.session.get(API_URL + '/core/profile')
    name = reply.json().get('first_name', None)
    return name


def get_user_status(s: UserStatus, *args):
    ...


def get_board_list(s: UserStatus, *args):
    reply = s.session.get(API_URL + '/goals/board/list')
    boards = (enumerate(reply.json(), start=1))
    reply_list = []
    s.present_boards = {}
    for num, b in boards:
        reply_list.append((num, b['title']))
        s.present_boards[num] = PresentItem(id=b['id'], title=b['title'])
    reply_str = 'Your available boards are:\n' \
                + '\n'.join(list(f'{bid}: {markdowned(title)}' for (bid, title) in reply_list)) \
                + '\nSelect a board with `/board \\<number\\>` command\\.'
    return reply_str


def get_categories_list(s: UserStatus, *args):
    board = f'?board={s.board.id}' if s.board else ''
    reply = s.session.get(API_URL + '/goals/goal_category/list' + board)
    cats = (enumerate(reply.json(), start=1))
    reply_list = []
    s.present_cats = {}
    for num, b in cats:
        reply_list.append((num, b['title']))
        s.present_cats[num] = PresentItem(id=b['id'], title=b['title'])
    reply_str = 'Your available categories are:\n' \
                + '\n'.join(list(f'{bid}: {markdowned(title)}' for (bid, title) in reply_list)) \
                + '\nSelect a category with `/cat \\<number\\>` command\\.'
    return reply_str


def get_goals_list(s: UserStatus, *args):
    cat = f'?category={s.category.id}' if s.category else ''
    reply = s.session.get(API_URL + '/goals/goal/list' + cat)
    goals = (enumerate(reply.json(), start=1))
    reply_list = []
    for num, b in goals:
        reply_list.append((num, b['title']))
        s.present_goals[num] = PresentItem(id=b['id'], title=b['title'])
    print(reply_list)
    reply_str = 'Your goals are:\n' \
                + '\n'.join(list(f'{cid}: {title}' for (cid, title) in reply_list))
    return reply_str


def get_board_role(s: UserStatus, num: int):
    reply = s.session.get(API_URL + f'/goals/board/{num}')
    contents = reply.json()
    role = 3
    for p in contents['participants']:
        if p['user'] == s.username:
            role = p['role']
    return role


def select_board(s: UserStatus, board=None):
    try:
        board = int(board) if board else 0
    except ValueError:
        return 'Please provide board number, not name\\.'

    if board:
        if board not in s.present_boards:
            return 'Board number unknown, please use an existing one\\.\n' + get_board_list(s)
        s.board = s.present_boards[board]

    if s.board:
        s.present_cats = {}
        s.board.role = get_board_role(s, s.board.id)

        return f'Working in board *{markdowned(s.board.title)}*\\.\n' \
               + role_string[s.board.role] + '\n'\
               + get_categories_list(s)

    else:
        return 'Board not selected\\.\n' + get_board_list(s)


def select_category(s: UserStatus, category=None):
    try:
        category = int(category) if category else 0
    except ValueError:
        return 'Please provide category number, not name\\.'

    if category:
        if category not in s.present_cats:
            return 'Category number unknown, please use an existing one\\.\n' + get_categories_list(s)
        s.category = s.present_cats[category]

    if s.category:
        return f'Working in category *{markdowned(s.category.title)}*\\.\n' \
               + role_string[s.board.role] + '\n' \
               + get_goals_list(s)
    else:
        return 'Category not selected\\.\n' + get_categories_list(s)


def select_goal(s: UserStatus, goal=None):
    try:
        goal = int(goal) if goal else 0
    except ValueError:
        return 'Please provide category number, not name\\.'

    if goal:
        if goal not in s.present_goals:
            return 'Goal number unknown, please use an existing one\\.\n' + get_goals_list(s)
        s.goal = s.present_goals[goal]

    if s.goal:
        return f'Working with goal *{markdowned(s.goal.title)}*\\.\n' \
               + role_string[s.board.role] + '\n'
    else:
        return 'Goal not selected\\.\n' + get_goals_list(s)