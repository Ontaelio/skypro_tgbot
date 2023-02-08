from api_views import *
from utils import unknown_command

commands = {
    '/boards': get_board_list,
    '/categories': get_categories_list,
    '/cats': get_categories_list,
    '/goals': get_goals_list,
    '/board': select_board,
    '/category': select_category,
    '/cat': select_category,
    '/goal': select_goal,
    '/comments': get_comments,
}


def get_help(*args):
    return str(f"Available commands: {', '.join(list(commands.keys()))}\\.")


def parse_command(words: list) -> callable:
    words = [word.lower() for word in words]
    com = words[0]
    args = words[1:] if len(words) > 1 else []
    if com == '/help':
        return get_help, args
    if com not in commands:
        return unknown_command, args
    return commands[com], args
