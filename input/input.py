

def ask_for_input(prompt, default_value=None, filter_function=lambda x: None if x == '' else x):
    if default_value is None:
        inp = input("{prompt}: ".format(prompt=prompt))
    else:
        inp = input("{prompt} ({default})".format(prompt=prompt, default=default_value))
    if inp == '' and default_value is not None:
        return default_value
    res = filter_function(inp)
    if res is not None:
        return res
    else:
        print('wrong formated input, please try again')
        return ask_for_input(prompt, default_value, filter_function)


def filter_tournament_id(x):
    return _filter_int(x, r"https://(?:(?:dev\.)?beta\.)?online-go.com(?::8080)?/tournament/([0-9]+)/?")


def filter_game_id(x):
    return _filter_int(x, r"https://(?:(?:dev\.)?beta\.)?online-go.com(?::8080)?/game(?:/view)?/([0-9]+)/?")


def _filter_int(x, regex_string):
    if x == '':
        return None
    try:
        i = int(x)
        return i
    except ValueError:
        import re
        r = re.compile(regex_string, re.IGNORECASE)
        m = r.match(x)
        if m is None:
            return None
        else:
            try:
                return int(m.group(1))
            except ValueError:
                return None
