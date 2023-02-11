# Telegram bot for Skypro Diploma


For some commands like changing names double quotes can be used.
Note that thus double quotes should NOT be used in comments and other places where they DO NOT form a complete argument.
(Although you _can_ enclose the entire comment in double quotes.)
Double quotes are supposed to happen ONLY at the end of a complex command.
### Commands
* /help - display a list of available commands
* /help \<command> - get help on a particular command
* /help verbose - get all commands and their descriptions

Lists and items:
* /boards [me | \<username]
* /board [\<num>]
* cats / categories
* cat / category [\<num>]
* /goals
* /goal [\<num>]
* /comments (when a goal is selected), see below.
* /users (when a board is selected). There's no way to get info on a particular user due to the way backend was done (as requested by the front).
* /me - get info on current user

Options for lists:
* all - display everything for /cats, /goals
* any - all statuses (only todo and active by default) for /goals
* todo, active, done - status selection for /goals
* low, normal, high, critical - priority selection for /goals

Mix options as you wish separated by space

When a goal is selected:
* /comments [\<qty>] [<\skip>], where optional \<qty> is the number of comments to display and \<skip> is how many to skip. Top comments are the latest ones. Defaults are 3 and 0.

DB manipulation:
* /create (board | cat | goal) \<name> - create stuff
* /rename [board | cat | goal] \<name>
* /comment \<text> - write a comment (in a goal)
* /me [name | first_name | last_name | email] \<data> [\<data2>] - edit your info
* /add \<username> [\<read> | <\write>] - add a user to your board
* /delete (board | category | goal) <"name">
* /remove <username>

With goals:
* /description \<"text"> - create a description for a goal
* /due \<YYYY-MM-DD> - create a due date
* /status \<num> | (todo | active | done | archived) - change status. Not that archived goals are gone
* /priority \<num> | (low | medium | high | critical) - set priority for a goal

### Text style coding

Statuses:
* ~~done~~ tasks are striken through
* todo tasks are normal
* **active** tasks are bold

Priorities:
* low and medium tasks are normal
* _high_ tasks are in italic
* critical tasks are underlined (can't show it here as normal MD doesn't support this)

These styles are combined in the output, thus an **_active high task_** will look like this.
