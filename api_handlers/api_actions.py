import requests

from api_handlers.api_views import get_comments
from api_handlers.utils import markdowned
from classes import UserStatus
from settings import API_URL


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
        return 'Please add arguments: `/create <board | cat | goal> <name>`\\.'
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
        reply = s.session.post(API_URL + '/goals/goal/create', data={'title': title, 'category': s.category.id})

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
