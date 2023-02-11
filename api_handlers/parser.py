from api_handlers.api_actions import *
from api_handlers.api_views import *
from api_handlers.utils import unknown_command

commands = {
    '/boards': get_board_list,
    '/categories': get_categories_list,
    '/goals': get_goals_list,

    '/board': select_board,
    '/category': select_category,
    '/goal': select_goal,

    '/create': create_item,
    '/rename': rename_item,
    '/delete': delete_item,

    '/comments': get_comments,
    '/comment': create_comment,
    '/description': set_goal_description,
    '/status': set_goal_status,
    '/priority': set_goal_priority,
    '/due': set_goal_due,

    '/users': get_users_list,
    '/me': get_change_my_details,
    '/add': add_user,
    '/remove': remove_user,

    '/connect': connect_and_create_code,
    '/verify': verify_user,
}

shortcuts = {
    '/cat': '/category',
    '/cats': '/categories',
    '/new': '/create',
}

keep_case = ['/me',
             '/comment',
             '/create',
             '/description',
             '/rename',
             '/add',
             '/delete',
]


def get_help(s, *args):
    """
Get help on a particular command or a list of available commands.
Usage: /help [<command>] | [verbose]
And yes, docstrings are used for /help, thus they look like this one.
    """

    if args:
        c = args[0] if args[0][0] == '/' else '/' + args[0]
        if c.lower() in ['/verbose', '/help']:
            return '\n'.join([f'{markdowned(_)}: {markdowned(f.__doc__)}' if f.__doc__
                              else f'{markdowned(_)}: No help yet\n'
                              for _, f in commands.items()])

        if c in shortcuts:
            c = shortcuts[c]

        if c in commands:
            if commands[c].__doc__:
                return markdowned(commands[c].__doc__)
            else:
                return 'For some strange reason this command does not have help yet\\.'

        return markdowned(f'Unknown command: {c}')

    return str(f"{s.name}, available commands are: {', '.join(list(commands.keys()))}\\.\n"
               f"Use `/help <command>` for detailed info\\.")


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
    if com in shortcuts:
        com = shortcuts[com]
    if com not in commands:
        return unknown_command, args
    return commands[com], args
