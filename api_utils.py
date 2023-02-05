import requests

from classes import UserStatus, PresentItem
from settings import API_URL


def unknown_command(*args):
    return 'Unknown command, check /help.'


def user_login(username, password):
    s = requests.Session()
    s.auth = (username, password)
    reply = s.get(API_URL + '/core/profile')
    if reply.status_code == 200:
        name = reply.json().get('first_name', None)
        return s, name
    return None, None


def get_user_name(s: UserStatus, *args):
    reply = s.session.get(API_URL + '/core/profile')
    name = reply.json().get('first_name', None)
    return name


def get_board_list(s: UserStatus, *args):
    reply = s.session.get(API_URL + '/goals/board/list')
    boards = (enumerate(reply.json(), start=1))
    reply_list = []
    s.present_boards = {}
    for num, b in boards:
        reply_list.append((num, b['title']))
        s.present_boards[num] = PresentItem(id=b['id'], title=b['title'])
    reply_str = 'Your available boards are:\n' \
                + '\n'.join(list(f'{bid}: {title}' for (bid, title) in reply_list)) \
                + '\nSelect a board with /board <number> command.'
    return reply_str


def get_categories_list(s: UserStatus, *args):
    board = f'?board={s.board.id}' if s.board else ''
    reply = s.session.get(API_URL + '/goals/goal_category/list' + board)
    # print(board)
    # print(reply.json())
    cats = reply.json()
    reply_list = [(r['id'], r['title']) for r in cats]
    reply_str = 'Your available categories are:\n' \
                'id: name\n' + '\n'.join(list(f'{cid}: {title}' for (cid, title) in reply_list))
    return reply_str


def get_goals_list(s: UserStatus, *args):
    reply = s.session.get(API_URL + '/goals/goal/list')
    goals = reply.json()
    reply_list = [(r['id'], r['title']) for r in goals]
    reply_str = 'Your goals are:\n' \
                'id: name\n' + '\n'.join(list(f'{cid}: {title}' for (cid, title) in reply_list))
    return reply_str


def select_board(s: UserStatus, board=None):
    try:
        board = int(board) if board else 0
    except ValueError:
        return 'Please provide board number, not name.'

    if board:
        if board not in s.present_boards:
            return 'Board number unknown, please use an existing one.\n' + get_board_list(s)
        s.board = s.present_boards[board]

    if s.board:
        return f'Working in board {s.board.title}.\n' + get_categories_list(s)
    else:
        return 'Board not selected.\n' + get_board_list(s)
