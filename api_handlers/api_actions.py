import requests

from api_handlers.api_views import get_comments, status_string, priority_string
from api_handlers.utils import markdowned
from classes import UserStatus
from settings import API_URL

status_int = {
    'todo': 1,
    'active': 2,
    'done': 3,
    'archived': 4,
}

priority_int = {
    'low': 1,
    'medium': 2,
    'high': 3,
    'critical': 4
}


def get_change_my_details(s: UserStatus, *args):
    reply = s.session.get(API_URL + '/core/profile')
    me = reply.json()

    if args:
        if args[0] == 'name':
            try:
                me['first_name'] = args[1]
                me['last_name'] = args[2]
            except IndexError:
                return f'Please provide two values for `/name <first> <last>`\\.'

        if args[0] in ['first_name', 'last_name', 'email']:
            try:
                me[args[0]] = args[1]
            except IndexError:
                return f'Please provide data for `/{args[0]} <data>`\\.'

        reply = s.session.put(API_URL + '/core/profile', data=me)
        if reply.status_code != 200:
            return 'Something went wrong, please check the data provided\\.'

    return markdowned('You are:\n'
                      + f"Username: {me['username']}\n"
                      + f"First name: {me['first_name']}\n"
                      + f"Last name: {me['last_name']}\n"
                      + f"e-mail: {me['email']}\n") \
           + "You may change some with `/me first_name <...>`, `/me last_name <...>`, `/me email <...>` or `/me name " \
             "<first> <last>`\\. "


def create_item(s: UserStatus, *args):
    if not args:
        return 'Please add arguments: `/create <board | cat | goal> <"name"> [<"description">]`\\.'
    command = args[0].lower()
    if command not in ['board', 'cat', 'category', 'goal']:
        return f'I don\'t know how to create a {args[0]}\\.'
    try:
        title = args[1]
    except IndexError:
        return f'Please provide a name for a new {args[0]}\\.'

    reply = ''
    if command == 'board':
        reply = s.session.post(API_URL + '/goals/board/create', data={'title': title})
    if command in ['cat', 'category']:
        if not s.board:
            return 'Please select a board first\\.'
        reply = s.session.post(API_URL + '/goals/goal_category/create', data={'title': title, 'board': s.board.id})
    if command == 'goal':
        if not s.category:
            return 'Please select a category first\\.'
        try:
            desc = args[2]
        except IndexError:
            desc = None
        reply = s.session.post(API_URL + '/goals/goal/create',
                               data={'title': title, 'category': s.category.id, 'description': desc})

    if reply.status_code not in [200, 201]:  # just in case
        return 'Something went wrong, sorry\\.'
    else:
        return f'{args[0].capitalize()} {markdowned(title)} created\\.'


def create_comment(s: UserStatus, *words):
    if not s.goal:
        return "Please select a goal to comment\\."
    if s.board.role not in [1, 2]:
        return 'You are not allowed to post comments here\\.'
    if not words:
        return "Please include the comment text after the `/comment` command\\."

    text = ' '.join(words)
    comment = {'goal': s.goal.id, 'text': text}
    reply = s.session.post(API_URL + '/goals/goal_comment/create', json=comment)
    if reply.status_code not in [200, 201]:  # just in case
        return 'Something went wrong, sorry\\.'

    return get_comments(s, '1', '0')


def set_goal_description(s: UserStatus, *words):
    if not s.goal:
        return "Please select a goal to describe\\."
    if s.board.role not in [1, 2]:
        return 'You are not allowed to edit on this board\\.'
    if not words:
        return 'Please provide a text\\.'

    desc = ' '.join(words)
    reply = s.session.patch(API_URL + f'/goals/goal/{s.goal.id}', data={'description': desc})
    if reply.status_code not in [200, 201]:  # just in case
        return 'Something went wrong, sorry\\.'

    s.goal.description = desc
    return 'Description updated\\.'


def set_goal_status(s: UserStatus, *status):
    value = 0
    if not status:
        return f'Current goal is {status_string[s.goal.status]} and is {priority_string[s.goal.priority]}\\.'
    if status[0] in ['1', '2', '3', '4']:
        value = int(status[0])
    elif status[0] in status_int:
        value = status_int[status[0]]

    print(value)

    reply = s.session.patch(API_URL + f'/goals/goal/{s.goal.id}', data={'status': value})
    if reply.status_code not in [200, 201]:  # just in case
        return 'Something went wrong, sorry\\.'
    s.goal.status = value
    return 'Status updated\\.'


def set_goal_priority(s: UserStatus, *priority):
    value = 0
    if not priority:
        return f'Current goal is {priority_string[s.goal.status]} and is {priority_string[s.goal.priority]}\\.'
    if priority[0] in ['1', '2', '3', '4']:
        value = int(priority[0])
    elif priority[0] in priority_int:
        value = priority_int[priority[0]]

    reply = s.session.patch(API_URL + f'/goals/goal/{s.goal.id}', data={'priority': value})
    if reply.status_code not in [200, 201]:  # just in case
        return 'Something went wrong, sorry\\.'
    s.goal.priority = value
    return 'Priority updated\\.'


def set_goal_due(s: UserStatus, *due_date):
    value = 0
    if not due_date:
        return f'Please provide a date in YYYY\\-MM\\-DD format\\.'
    value = due_date[0]

    reply = s.session.patch(API_URL + f'/goals/goal/{s.goal.id}', data={'due_date': value})
    if reply.status_code not in [200, 201]:  # just in case
        return 'Something went wrong, sorry\\. Maybe wrong date format?'
    s.goal.due_date = value
    return 'Due date updated\\.'
