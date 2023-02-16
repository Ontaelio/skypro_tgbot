from typing import Callable
from functools import wraps

from exceptions import *


def rights_owner(func) -> Callable:
    @wraps(func)
    def _wrapper(s, *args):
        if not s.board:
            raise NotInBoard
        if s.board.role != 1:
            raise NotAnOwner
        return func(s, *args)
    return _wrapper


def rights_editor(func) -> Callable:
    @wraps(func)
    def _wrapper(s, *args):
        if not s.board:
            raise NotInBoard
        if s.board.role not in [1, 2]:
            raise NotAnEditor
        return func(s, *args)
    return _wrapper


def level_board(func) -> Callable:
    @wraps(func)
    def _wrapper(s, *args):
        if not s.board:
            raise NotInBoard
        return func(s, *args)
    return _wrapper


def level_category(func) -> Callable:
    @wraps(func)
    def _wrapper(s, *args):
        if not s.category:
            raise NotInCategory
        return func(s, *args)
    return _wrapper


def level_goal(func) -> Callable:
    @wraps(func)
    def _wrapper(s, *args):
        if not s.goal:
            raise NotInGoal
        return func(s, *args)
    return _wrapper


def args_required(func) -> Callable:
    @wraps(func)
    def _wrapper(s, *args):
        if not args:
            raise ArgsMissing(func.__doc__)
        return func(s, *args)
    return _wrapper


def number_or_none(func) -> Callable:
    @wraps(func)
    def _wrapper(s, *args):
        try:
            num = int(args[0])
        except ValueError:
            raise NonIntArgs
        except IndexError:
            num = None
        return func(s, num)
    return _wrapper
