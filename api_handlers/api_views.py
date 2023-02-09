import requests

from classes import UserStatus, PresentItem
from settings import API_URL
from api_handlers.utils import markdowned, find_board_local_id, get_category_board, get_board_role, get_user_name, get_goal_details, \
    get_category_details, find_cat_local_id

role_string = {
    1: 'You *own* this place\\!',
    2: 'You can *write and edit* here\\.',
    3: 'You are a *reader* here\\.'
}

status_string = {
    1: 'Todo',
    2: '*Active*',
    3: '~Done~',
    4: '~Archived~'
}

priority_string = {
    1: 'Low',
    2: 'Medium',
    3: '_High_',
    4: '__Critical__'
}

status_md = {
    'archived': '',
    'done': '~',
    'todo': '',
    'active': '*',
}

priority_md = {
    'low': '',
    'medium': '',
    'high': '_',
    'critical': '\r__'
}


def user_login(username, password):
    s = requests.Session()
    s.auth = (username, password)
    reply = s.get(API_URL + '/core/profile')
    if reply.status_code == 200:
        name = reply.json().get('first_name', None)
        user_id = reply.json().get('id')
        return s, name, user_id
    return None, None, None


# ************** Lists **************

def get_board_list(s: UserStatus, *args):
    reply = s.session.get(API_URL + '/goals/board/list')
    boards = (enumerate(reply.json(), start=1))
    reply_list = []
    s.present_boards = {}
    for num, b in boards:
        reply_list.append((num, b['title']))
        s.present_boards[num] = PresentItem(id=b['id'], title=b['title'])
    s.default_command = '/board'
    reply_str = 'Your available boards are:\n' \
                + '\n'.join(list(f'{bid}: {markdowned(title)}' for (bid, title) in reply_list)) \
                + '\nSelect a board by it\'s \\# or with `\\/board \\<number\\>`'
    return reply_str


def get_categories_list(s: UserStatus, *args):
    if 'all' in args:
        s.board = None
        s.category = None
    board = f'?board={s.board.id}' if s.board else ''
    reply = s.session.get(API_URL + '/goals/goal_category/list' + board)
    cats = (enumerate(reply.json(), start=1))
    reply_list = []
    s.present_cats = {}
    for num, b in cats:
        reply_list.append((num, b['title']))
        s.present_cats[num] = PresentItem(id=b['id'], title=b['title'])
    s.default_command = '/category'
    reply_str = 'Your available categories are:\n' \
                + '\n'.join(list(f'{bid}: {markdowned(title)}' for (bid, title) in reply_list)) \
                + '\nSelect a category by it\'s \\# or with `/cat \\<number\\>`'
    return reply_str


def get_goals_list(s: UserStatus, *args):
    if 'all' in args:
        s.board = None
        s.category = None
    if 'any' in args:
        statuses = ['todo', 'active', 'done', 'archived']
    else:
        statuses = args if any(s in args for s in ['todo', 'active', 'done', 'archived']) else ['todo', 'active']
    priorities = args if any(s in args for s in ['low', 'medium', 'high', 'critical'])\
        else ['low', 'medium', 'high', 'critical']

    cat = f'?category={s.category.id}' if s.category else ''
    reply = s.session.get(API_URL + '/goals/goal/list' + cat)
    goals = (enumerate(reply.json(), start=1))
    reply_list = []
    s.present_goals = {}

    for num, b in goals:
        status = status_string[b['status']].lower().strip('_*~')
        priority = priority_string[b['priority']].lower().strip('_*~')
        print(b['title'])
        if status in statuses and priority in priorities:
            smd = status_md[status]
            pmd = priority_md[priority]
            # if not any([smd, pmd]):
            b['title'] = markdowned(b['title'])

            reply_list.append(f"{num}: {smd}{pmd}{b['title']}{pmd}{smd}")
        s.present_goals[num] = PresentItem(id=b['id'], title=b['title'])
    s.default_command = '/goal'

    reply_str = 'Your goals are:\n' \
                + '\n'.join(reply_list) \
                + '\nSelect a goal by it\'s \\# or with `/goal \\<number\\>`'
    return reply_str


def get_users_list(s: UserStatus, *args):
    if not s.board:
        return 'Please select a board first\\.'

    reply = s.session.get(API_URL + f'/goals/board/{s.board.id}')
    users = reply.json()['participants']
    owners = []
    editors = []
    readers = []

    for user in users:
        person = {'id': user['id'],
                  'username': markdowned(user['user'])}
        if user['user'] == s.username:
            person['username'] = '*YOU*'
        if user['role'] == 1:
            owners.append(person)
        elif user['role'] == 2:
            editors.append(person)
        else:
            readers.append(person)

    userlist = f'Board {markdowned(s.board.title)} participants are:\n'\
                + '*Owner*:\n'\
                + f"{owners[0]['id']}: {owners[0]['username']}\n\n"\
                + '*Editors*\n'\
                + '\n'.join(f"{editor['id']}: {editor['username']}" for editor in editors) + '\n\n'\
                + '*Readers*\n' \
                + '\n'.join(f"{reader['id']}: {reader['username']}" for reader in readers)
    print('AND ME IS:', s.id)

    return userlist


def get_comments(s: UserStatus, *args):
    if not s.goal:
        return 'Please select a goal'

    limit = 3
    offset = 0
    if args:
        if args[0].isdecimal():
            limit = int(args[0])
        if len(args) > 1:
            if args[1].isdecimal():
                offset = int(args[1])

    reply = s.session.get(API_URL + f'/goals/goal_comment/list?goal={s.goal.id}&limit={limit}&offset={offset}')
    comments = reply.json()['results']
    count = int(reply.json()['count'])

    if not comments:
        return 'No comments here yet\\.'

    if offset:
        message = [f'There are *{count}* comments, displaying {limit} starting with {offset+1}']
    else:
        if limit >= count:
            message = ['Here are all the comments:']
        else:
            message = [f'There are *{count}* comments, displaying the first {limit}']

    for comment in comments:
        if comment['user']['id'] == s.id:
            user = '*YOU*'
        else:
            if comment['user']['first_name']:
                user = markdowned(comment['user']['first_name'] + ' ' + str(comment['user']['last_name']))
            else:
                user = markdowned(comment['user']['username'])
        message.append(user + ': ' + markdowned(comment['text']))

    return '\n'.join(message)


# ************** Select Items **************

def select_board(s: UserStatus, *board):
    try:
        board = int(board[0])
    except ValueError:
        return 'Please provide board number, not name\\.'
    except IndexError:
        board = 0

    if board:
        if board not in s.present_boards:
            return 'Board number unknown, please use an existing one\\.\n' + get_board_list(s)
        s.board = s.present_boards[board]

    if s.board:
        s.present_goals = {}
        s.board.role = get_board_role(s, s.board.id)
        s.default_command = '/category'

        return f'Working in board *{markdowned(s.board.title)}*\\.\n' \
               + role_string[s.board.role] + '\n' \
               + get_categories_list(s)

    else:
        return 'Board not selected\\.\n' + get_board_list(s)


def select_category(s: UserStatus, *category):
    try:
        category = int(category[0])
    except ValueError:
        return 'Please provide category number, not name\\.'
    except IndexError:
        category = 0

    if category:
        if category not in s.present_cats:
            return 'Category number unknown, please use an existing one\\.\n' + get_categories_list(s)
        s.category = s.present_cats[category]

    if s.category:
        message = ''
        if not s.board:
            b = get_category_board(s)
            get_board_list(s, None)
            board_id = find_board_local_id(s, b)
            select_board(s, board_id)
            message = f'Switched to board *{markdowned(s.board.title)}*\\.\n'

        s.default_command = '/goal'

        return message \
               + f'Working in category *{markdowned(s.category.title)}*\\.\n' \
               + role_string[s.board.role] + '\n' \
               + get_goals_list(s)
    else:
        return 'Category not selected\\.\n' + get_categories_list(s)


def select_goal(s: UserStatus, *goal):
    try:
        goal = int(goal[0])
    except ValueError:
        return 'Please provide category number, not name\\.'
    except IndexError:
        goal = 0

    if goal:
        if goal not in s.present_goals:
            return 'Goal number unknown, please use an existing one\\.\n' + get_goals_list(s)
        s.goal = get_goal_details(s, s.present_goals[goal].id)

    if s.goal:
        message = ''
        if not s.category:
            s.board = None
            get_categories_list(s, None)
            cat_id = find_cat_local_id(s, s.goal.category)
            select_category(s, cat_id)
            message = f'Switched to board *{markdowned(s.board.title)}*\\.\n' \
                      + f'Selected category *{markdowned(s.category.title)}*\\.\n'

        return message + f'Working with goal:\n*{markdowned(s.goal.title)}*\n' \
               + (f'_{markdowned(s.goal.description)}_\n' if s.goal.description else '') \
               + (f'Due on {markdowned(s.goal.due_date)}\n' if s.goal.due_date else 'Due date not set\n') \
               + 'Status: ' + status_string[s.goal.status] + '\n' \
               + f'Priority: {priority_string[s.goal.priority]}\n' \
               + role_string[s.board.role] + '\n'
    else:
        return 'Goal not selected\\.\n' + get_goals_list(s)
