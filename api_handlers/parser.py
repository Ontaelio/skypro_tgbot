from api_handlers.api_actions import *
from api_handlers.api_views import *
from api_handlers.utils import unknown_command

commands = {
    '/boards': get_board_list,
    '/categories': get_categories_list,
    '/cats': get_categories_list,
    '/users': get_users_list,
    '/goals': get_goals_list,
    '/board': select_board,
    '/category': select_category,
    '/cat': select_category,
    '/goal': select_goal,
    '/comments': get_comments,

    '/comment': create_comment,
    '/me': get_change_my_details,
    '/create': create_item,
}

keep_case = ['/me',
             '/comment',
             '/create',
             ]


def get_help(*args):
    return str(f"Available commands: {', '.join(list(commands.keys()))}\\.")


def split_double_quoted(s_in: str) -> list:
    s = s_in.split('"')
    if len(s) == 1:
        return s[0].split()
    return list(filter(lambda n: n not in ['', ' '], s[0].split() + s[1:]))


def parse_command(words: list) -> callable:
    com = words[0].lower()
    if com not in keep_case:
        words = [word.lower() for word in words]
    args = words[1:] if len(words) > 1 else []
    if com == '/help':
        return get_help, args
    if com not in commands:
        return unknown_command, args
    return commands[com], args
