import random
import string

import requests

from api_handlers.api_views import get_comments, status_string, priority_string
from api_handlers.decorators import rights_editor, level_goal, level_board, rights_owner, args_required, level_category
from api_handlers.utils import markdowned
from classes import UserStatus
from settings import API_URL, users

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
    """
Get / change current user details (first name, last name and email)
Usage: /me
Or: /me name <first name> <last name>
Or: /me first_name <first name> | last_name <last name> | email <email>
* Use double quotes for compound names, e.g. /me name "Anna Maria" "von Appelbaum"
    """

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
            return f'Something went wrong, please check the data provided\\. Code {reply.status_code}\\.'

    return markdowned('You are:\n'
                      + f"Username: {me['username']}\n"
                      + f"First name: {me['first_name']}\n"
                      + f"Last name: {me['last_name']}\n"
                      + f"e-mail: {me['email']}\n")


def create_item(s: UserStatus, *args):
    """
Create a new board, category or goal
Usage: /create (board | category | goal) <name>
* Use double quotes for compound names, e.g. /create goal "Make something great again"
* category can be shortened to cat
    """

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
        if reply.status_code == 403:
            return f'You don\'t have the rights to create a {args[0]} here\\.'
        return f'Something went wrong, sorry\\. Code: {reply.status_code}\\.'
    else:
        return f'{args[0].capitalize()} {markdowned(title)} created\\.'


@rights_editor
@args_required
def rename_item(s: UserStatus, *words):
    """
Set a new name for the current board, category or goal
Usage: /rename [board | cat | goal] <name>
* If board/cat/goal is omitted, the current item's name will be changed (EXPERIMENTAL!)
* Use double quotes for compound names.
    """

    arg = words[0]
    url, target = '', ''

    if arg in ['board', 'cat', 'category', 'goal']:
        try:
            title = words[1]
        except IndexError:
            return 'Provide a title please\\.'
        if arg == 'board':
            if not s.board:
                return 'You must be in a board to rename it\\.'
            url = f'/goals/board/{s.board.id}'
            target = 'Board'
        if arg in ['cat', 'category']:
            if not s.category:
                return 'You must be in a category to rename it\\.'
            url = f'/goals/goal_category/{s.category.id}'
            target = 'Category'
        if arg == 'goal':
            if not s.goal:
                return 'You must be in a goal to rename it\\.'
            url = f'/goals/goal/{s.goal.id}'
            target = 'Goal'

    else:
        # now this is extremely experimental
        if s.goal:
            url = f'/goals/goal/{s.goal.id}'
            target = 'Goal'
        elif s.category:
            url = f'/goals/goal_category/{s.category.id}'
            target = 'Category'
        else:
            url = f'/goals/board/{s.board.id}'
            target = 'Board'
        title = words[0]

    reply = s.session.patch(API_URL + url, data={"title": title})
    if reply.status_code not in [200, 201]:  # just in case
        if reply.status_code == 403:
            return 'Forbidden\\. Only board owners can edit them\\.'
        return f'Something went wrong, sorry\\. Code: {reply.status_code}\\.'

    match target:
        case 'Board':
            s.board.title = title
        case 'Category':
            s.category.title = title
        case 'Goal':
            s.category.goal = title
    return f'{target} name changed to {markdowned(title)}\\.'


@level_goal
@rights_editor
def create_comment(s: UserStatus, *words):
    """
Add a comment to the selected goal
Usage: /comment <text>
Double quotes are not necessary.
    """

    if not words:
        return "Please include the comment text after the `/comment` command\\."

    text = ' '.join(words)
    comment = {'goal': s.goal.id, 'text': text}
    reply = s.session.post(API_URL + '/goals/goal_comment/create', json=comment)
    if reply.status_code not in [200, 201]:  # just in case
        return f'Something went wrong, sorry\\. Code: {reply.status_code}\\.'

    return get_comments(s, '1', '0')


@level_goal
@rights_editor
def set_goal_description(s: UserStatus, *words):
    """
Set or get the selected goal's description
Usage: /description [<new_text>]
Double quotes are not necessary.
    """

    if not words:
        return f'_{markdowned(s.goal.description)}_'

    desc = ' '.join(words)
    reply = s.session.patch(API_URL + f'/goals/goal/{s.goal.id}', data={'description': desc})
    if reply.status_code not in [200, 201]:  # just in case
        return f'Something went wrong, sorry\\. Code: {reply.status_code}\\.'

    s.goal.description = desc
    return 'Description updated\\.'


@level_goal
@rights_editor
def set_goal_status(s: UserStatus, *status):
    """
Set the selected goal's status
Usage: /status <num> | (todo | active | done | archived)
* num is 1, 2 or 3 for todo, active and done. Use either numbers of words.
* Note: archived will delete the goal! You will be able to restore it by changing it's status while it is still selected.
    """
    value = 0
    if not status:
        return f'Current goal is {status_string[s.goal.status]} and is {priority_string[s.goal.priority]}\\.'
    if status[0] in ['1', '2', '3']:
        value = int(status[0])
    elif status[0] in status_int:
        value = status_int[status[0]]

    reply = s.session.patch(API_URL + f'/goals/goal/{s.goal.id}', data={'status': value})
    if reply.status_code not in [200, 201]:  # just in case
        return f'Something went wrong, sorry\\. Code: {reply.status_code}\\.'
    s.goal.status = value
    return f'Status updated to {status_string[s.goal.status]}\\.'


@level_goal
@rights_editor
def set_goal_priority(s: UserStatus, *priority):
    """
Set the selected goal's priority
Usage: /status <num> | (low | medium | high | critical)
* use either words ot numbers 1, 2, 3 or 4.
    """

    value = 0
    if not priority:
        return f'Current goal is {status_string[s.goal.status]} and is {priority_string[s.goal.priority]}\\.'
    if priority[0] in ['1', '2', '3', '4']:
        value = int(priority[0])
    elif priority[0] in priority_int:
        value = priority_int[priority[0]]

    reply = s.session.patch(API_URL + f'/goals/goal/{s.goal.id}', data={'priority': value})
    if reply.status_code not in [200, 201]:  # just in case
        return f'Something went wrong, .sorry Code: {reply.status_code}\\.'
    s.goal.priority = value
    return f'Priority updated to {priority_string[s.goal.priority]}\\.'


@level_goal
@rights_editor
def set_goal_due(s: UserStatus, *due_date):
    """
Sets the due date for a goal.
Usage: /due <YYYY-MM-DD>
A goal must be selected.
    """

    if not due_date:
        return f'Due on: *{markdowned(s.goal.due_date)}*'

    value = due_date[0]

    reply = s.session.patch(API_URL + f'/goals/goal/{s.goal.id}', data={'due_date': value})
    if reply.status_code not in [200, 201]:  # just in case
        if reply.status_code == 400:
            return 'Seems like a wrong date, please check the format: YYYY\\-MM\\-DD format\\.'
        return f'Something went wrong, sorry\\. Code {reply.status_code}\\.'
    s.goal.due_date = value

    return f'Due date updated to {s.goal.due_date}\\.'


@level_board
@rights_owner
@args_required
def add_user(s: UserStatus, *args):
    """
Add a user to current board.
Usage: /add <username> [read | write]
Defaults to read.
    """

    user = args[0]
    role = args[1][0].lower if len(args) > 1 else 'r'
    if role not in ['r', 'w']:
        return add_user.__doc__
    role_num = 2 if role == 'w' else 3

    reply = s.session.patch(API_URL + f'/goals/board/{s.board.id}',
                            json={"participants": [{"user": user, "role": role_num}]})

    if reply.status_code not in [200, 201]:  # just in case
        if reply.status_code == 400:
            return markdowned(f'Error: User {user} does not exist.')
        return f'Something went wrong, sorry\\. Code: {reply.status_code}\\.'

    return markdowned(f'User {user} added to board {s.board.title}.')


@rights_owner
def delete_board(s: UserStatus, title):
    # if not s.board:
    #     return 'You must select a board with `/board <num>` to delete it\\.'
    reply = s.session.delete(API_URL + f'/goals/board/{s.board.id}')
    if reply.status_code == 204:
        s.board = None
        return markdowned(f'Board "{title}" deleted')
    else:
        return markdowned(f'Was not able to delete "{title}". Error code: {reply.status_code}')


@level_category
@rights_owner
def delete_category(s: UserStatus, title):
    reply = s.session.delete(API_URL + f'/goals/goal_category/{s.category.id}')
    if reply.status_code == 204:
        s.category = None
        s.goal = None
        return markdowned(f'Category "{title}" deleted')
    else:
        return markdowned(f'Was not able to delete "{title}". Error code: {reply.status_code}')


@level_goal
@rights_owner
def delete_goal(s: UserStatus):
    # if not s.goal:
    #     return 'You must select a goal with `/goal <num>` to delete it\\.'
    return set_goal_status(s, 'archived')


def delete_comment(s: UserStatus, args):
    # using try-except approach for fun here
    try:
        reply = s.session.delete(API_URL + f'/goals/goal_comment/{s.present_comments[int(args[1])]}')
    except IndexError:
        return 'Please provide a comment number\\.'
    except ValueError:
        return 'Please use comment number, not name\\.'
    except KeyError:
        return 'Please use `/comments` to get a comments list with valid comment numbers\\.'
    if reply.status_code == 204:
        return 'Comment deleted\\.'
    else:
        return f'Something went wrong, code {reply.status_code}'


@level_board
@args_required
def delete_item(s: UserStatus, *args):
    """
Delete board, category or goal
Usage: /delete (board | category | goal | comment) <"name">
* Must be an owner (author for comments)
* Must be in the board/category/goal about to be deleted
* WARNING: Once deleted, boards and categories stay deleted! Hence the <name>.
* Goals can be restored by setting their status to 1/2/3 before another goal is selected. Then they are gone.
* <name> is needed only for boards and categories, as they are deleted immediately.
    """

    if args[0] not in ['board', 'category', 'goal', 'comment']:
        return f'Can not delete {markdowned(args[0])}\\. Note that case matters in `/delete`\\.'

    reply = ''
    match args[0]:
        case 'comment':
            return delete_comment(s, args)
        case 'goal':
            return delete_goal(s)

    title = s.board.title if args[0] == 'board' else s.category.title

    try:
        if args[1] != title:
            raise IndexError
    except IndexError:
        return markdowned(f'You must provide a correct {args[0]} name to delete it. Don\'t forget double quotes!')

    match args[0]:
        case 'board':
            return delete_board(s, title)
        case 'category':
            return delete_category(s, title)

    return 'This is message should never be seen (delete)'


@level_board
@rights_owner
@args_required
def remove_user(s: UserStatus, *args):
    """
Remove a user from current board
Usage: /remove <username>
* use /users to get the list of participants' usernames
    """

    bad_guy_name = args[0]
    if bad_guy_name == s.username:
        return 'You can not remove yourself, you own this board!'
    reply = s.session.get(API_URL + f'/goals/board/{s.board.id}')
    participants = [{'user': p['user'], 'role': p['role']} for p in reply.json()['participants']
                    if p['user'] not in [bad_guy_name, s.username]]

    reply = s.session.put(API_URL + f'/goals/board/{s.board.id}',
                          json={"title": s.board.title, "participants": participants})

    if reply.status_code not in [200, 201]:  # just in case
        return f'Something went wrong, sorry\\. Code: {reply.status_code}\\.'

    return f'User {bad_guy_name} participates in board {markdowned(s.board.title)} no longer\\.'


def logout(s: UserStatus, *args):
    """
    Log out a user logged in with /login command
    Usage: /logout
    * If this Telegram account is bound this command won't have any effect, use /unbind instead.
    """
    del users[s.tg_user]
    return 'Logged out\\.'


def unbind(s: UserStatus, *args):
    """
Log out and unbind this Telegram account.
Usage: /unbind
* This command is mostly for testing purposes, use only if you know what you are doing.
    """

    reply = s.session.delete(API_URL + f'/bot/delete/{s.tg_user}')
    if reply.status_code == 204:
        del users[s.tg_user]
        return 'This Telegram account is no longer bound to the app\\.'
    if reply.status_code == 404:
        return 'This account is not bound\\.'
    return f'Something went wrong\\. Code {reply.status_code}\\.'


def connect_and_create_code_placeholder():
    """
Create a verification code to bind this Telegram account with the app user
Usage: /bind
Open the web app and enter the code generated.
    """
    return markdowned('This should never be seen, this is a placeholder for help (/bind)')


# def verify_user(s: UserStatus, *args):
#     """
# Verify account
# Usage: /verify
# Once you entered the code generated with /connect in the web app run this to bind accounts.
#     """
#     if not s.code:
#         return 'Run /connect first\\.'
#
#     return 'Not implemented'
