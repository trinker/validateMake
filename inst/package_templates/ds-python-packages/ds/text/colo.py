import pyperclip


def colo(*regexes, fail: str = None, copy2clip: bool = False):
    """Make Regex to Locate Strings Containing Co-ocuring Substrings

    Make a regex to locate strings that contain >= 2 substrings with optional
    negation.

    Parameters:
        *regexes: Terms that cooccur/collocate
        fail: A substring to exclude from consideration.
        copy2clip: If True coppies the resulting regex to the clipboard.
                   This option is most useful when trying
                   to build a list regular expression model for easy pasting between testing
                   a regex and putting it into the model.

    Returns:
        Returns a regular expression.

    Examples::

        import pandas as pd
        from ds.text import colo

        colo('cat', 'dog', 'fish')
        colo('cat', 'dog', 'fish', fail = 'I Wish')
        colo('cat', 'fish')
        colo('cat', 'fish', fail = None)
        colo('cat', 'fish', fail = 'I Wish')
        colo('cat')
        colo('cat', fail = 'I Wish')
        colo('cat\\b', 'fish(\\b|es)')

        ## Make a dictionary of those patterns so we can see them in action
        patterns = {
            "colo('cat', 'dog', 'fish')": colo('cat', 'dog', 'fish'),
            "colo('cat', 'dog', 'fish', fail = 'I Wish')": colo('cat', 'dog', 'fish', fail = 'I Wish'),
            "colo('cat', 'fish')": colo('cat', 'fish'),
            "colo('cat', 'fish', fail = 'I Wish')": colo('cat', 'fish', fail = 'I Wish'),
            "colo('cat')": colo('cat'),
            "colo('cat', fail = 'I Wish')": colo('cat', fail = 'I Wish'),
            "colo('cat\\b', 'fish(\\b|es)')": colo('cat\\b', 'fish(\\b|es)')
        }


        x = pd.Series([
            'I have a cat, dog, fish & chicken',
            'I have a cat and fish.',
            'I have a cat and fished',
            'I have a dog, cat, fish!',
            'I Wish I had a cat, dog, and a fish',
            "I don't have a cat, dog, or fish",
            "I have a turtle",
            None
        ])


        for i, (input, pattern) in enumerate(patterns.items()):
            if i > 0:
                # no need to escape the slash if copying directly from the docstring
                print('\\n')
            print(
                # no need to escape the slash if copying directly from the docstring
                str(i + 1) + '. ' + input + ' -> "' + pattern + '"\\n',
                pd.DataFrame({'text': x, 'match': x.str.contains(pattern, regex = True).astype(str) })
            )
    """
    if copy2clip is None:
        copy2clip = False

    if fail is None:
        if len(regexes) == 1:

            if copy2clip:
                pyperclip.copy('"' + regexes[0].replace("\\", "\\\\") + '"')

            return regexes[0]

        else:
            return _cooc(*regexes, copy2clip=copy2clip)

    else:

        return _cooc_fail(*regexes, fail=fail, copy2clip=copy2clip)


def _cooc(*regexes, copy2clip):

    if len(regexes) == 2:
        z = "(({}.*{})|({}.*{}))".format(regexes[0], regexes[1], regexes[1], regexes[0])
    else:
        z = "^" + "".join(["(?=.*{})".format(regex) for regex in regexes])

    if copy2clip:
        pyperclip.copy('"' + z.replace("\\", "\\\\") + '"')

    return z


def _cooc_fail(*regexes, fail, copy2clip):

    z = "^(?!.*({}))".format(fail) + "".join(
        ["(?=.*({}))".format(regex) for regex in regexes]
    )
    if copy2clip:
        pyperclip.copy('"' + z.replace("\\", "\\\\") + '"')

    return z
