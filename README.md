# Telegram bot for Skypro Diploma


For some commands like changing names double quotes can be used.
Note that thus double quotes should NOT be used in comments and other places where they DO NOT form a complete argument.
(Although you _can_ enclose the entire comment in double quotes.)
Double quotes are supposed to happen ONLY at the end of a complex command.
### Commands
* /boards
* /board [\<num>]
* cats / categories
* cat / category [\num]
* /goals
* /goal [\num]
* /comments (when a goal is selected)
* /users (when a board is selected). There's no way to get info on a particular user due to the way backend was done (as requested by the front).

Note: /cat and /goal will return you back to the working category or goal if you used /boards or /cats to check the upper tree, unless the all option was used (see below).

options for lists:
* all - clear working tree, display everything for /cats, /goals
* any - all statuses (only todo and active by default) for /goals
* todo, active, done - status selection for /goals
* low, normal, high, critical - priority selection for /goals

Mix options as you wish separated by space

When a goal is selected:
* /comments [qty] [skip], where optional [qty] is the number of comments to display and [skip] is how many to skip. Top comments are the latest ones. Defaults are 3 and 0.

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