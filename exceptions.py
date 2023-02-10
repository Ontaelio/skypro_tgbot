class CommandUnavailable(Exception):
    pass


class NotAnOwner(CommandUnavailable):
    def __init__(self):
        message = 'You must be an owner to do this.'
        super().__init__(message)


class NotAnEditor(CommandUnavailable):
    def __init__(self):
        message = 'You must be an owner or an editor to do this.'
        super().__init__(message)


class NotInBoard(CommandUnavailable):
    def __init__(self):
        message = 'Please select a board first.'
        super().__init__(message)


class NotInCategory(CommandUnavailable):
    def __init__(self):
        message = 'Please select a category first.'
        super().__init__(message)


class NotInGoal(CommandUnavailable):
    def __init__(self):
        message = 'Please select a goal first.'
        super().__init__(message)


class ArgsMissing(CommandUnavailable):
    def __init__(self, help_string):
        message = help_string
        super().__init__(message)


class NonIntArgs(CommandUnavailable):
    def __init__(self):
        message = 'Please provide a number, not a name.'
        super().__init__(message)

# 365951089