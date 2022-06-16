import re
import pandas as pd


def to_snake(dataframe):
    """Rename DataFrame Columns to Snake Case

    Examples::

        dat4 = pd.DataFrame({
            'HelloWorld': [1, 2],
            'good_bye_world': ['a', 'b'],
            "Back World": [1, 2],
            'Another_World': ['a', 'b'],
            'Last  world': [5, 6]
        })


        to_snake(dat4)
        to_camel(dat4)
        to_camel(dat4, upper = False)
        to_space(dat4)
        to_space(dat4, upper = False)
    """
    dataframe = space_to_snake(camel_to_snake(dataframe))
    dataframe.columns = dataframe.columns.str.replace("_+", "_", regex=True)
    return dataframe


def to_camel(dataframe, upper=True):
    """Rename DataFrame Columns to Camel Case

    Parameters:
        dataframe: A Pandas DataFrame
        upper: If True, then the first letter of the string is capitalized (Upper Camel Case) otherwise it is lower (Lower Camel Case)

    Examples::

        dat4 = pd.DataFrame({
            'HelloWorld': [1, 2],
            'good_bye_world': ['a', 'b'],
            "Back World": [1, 2],
            'Another_World': ['a', 'b'],
            'Last  world': [5, 6]
        })


        to_snake(dat4)
        to_camel(dat4)
        to_camel(dat4, upper = False)
        to_space(dat4)
        to_space(dat4, upper = False)
    """
    dataframe = snake_to_space(dataframe)
    dataframe.columns = _to_title_camel(dataframe.columns)
    if not upper:
        dataframe.columns = dataframe.columns.map(lambda x: _onedown(x, True))

    return dataframe


def to_space(dataframe, upper=True):
    """Rename DataFrame Columns to Space Case

    Parameters:
        dataframe: A Pandas DataFrame
        upper: If True, then the letter after a space/string begining (a space is created ex nihilo from before uppers
               in a camel case or by converting underscore in snake case) is capitalized otherwise it is what ever format
               it was prior

    Examples::

        dat4 = pd.DataFrame({
            'HelloWorld': [1, 2],
            'good_bye_world': ['a', 'b'],
            "Back World": [1, 2],
            'Another_World': ['a', 'b'],
            'Last  world': [5, 6]
        })


        to_snake(dat4)
        to_camel(dat4)
        to_camel(dat4, upper = False)
        to_space(dat4)
        to_space(dat4, upper = False)
    """
    dataframe = camel_to_space(snake_to_space(dataframe))
    dataframe.columns = dataframe.columns.str.replace("\\s+", " ", regex=True)
    if upper:
        dataframe.columns = _to_title(dataframe.columns)
    return dataframe


def space_to_camel(dataframe, upper=True):
    """Rename DataFrame Columns

    Uses the heuristic current_to_desired case format

    Examples::

        dat = pd.DataFrame({'HelloWorld': [1, 2], 'GoodByeWorld': ['a', 'b']})
        camel_to_snake(dat)
        camel_to_space(dat)

        dat2 = camel_to_snake(dat); dat2
        snake_to_space(dat2)
        snake_to_camel(dat2)
        snake_to_camel(dat2, upper = False)

        dat3 = camel_to_space(dat); dat3
        space_to_snake(dat3)
        space_to_camel(dat3)
        space_to_camel(dat3, upper = False)

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    return dataframe.rename(
        columns={
            elem: _onedown(
                re.sub(r"(_|-)+", " ", elem).title().replace(" ", ""), (not upper)
            )
            for elem in dataframe.columns
        },
        inplace=False,
    )


def snake_to_camel(dataframe, upper=True):
    """Rename DataFrame Columns

    Uses the heuristic current_to_desired case format

    Examples::

        dat = pd.DataFrame({'HelloWorld': [1, 2], 'GoodByeWorld': ['a', 'b']})
        camel_to_snake(dat)
        camel_to_space(dat)

        dat2 = camel_to_snake(dat); dat2
        snake_to_space(dat2)
        snake_to_camel(dat2)
        snake_to_camel(dat2, upper = False)

        dat3 = camel_to_space(dat); dat3
        space_to_snake(dat3)
        space_to_camel(dat3)
        space_to_camel(dat3, upper = False)

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    return dataframe.rename(
        columns={
            elem: _onedown(
                re.sub(r"( |-)+", "_", elem).title().replace("_", ""), (not upper)
            )
            for elem in dataframe.columns
        },
        inplace=False,
    )


def camel_to_space(dataframe):
    """Rename DataFrame Columns

    Uses the heuristic current_to_desired case format

    Examples::

        dat = pd.DataFrame({'HelloWorld': [1, 2], 'GoodByeWorld': ['a', 'b']})
        camel_to_snake(dat)
        camel_to_space(dat)

        dat2 = camel_to_snake(dat); dat2
        snake_to_space(dat2)
        snake_to_camel(dat2)
        snake_to_camel(dat2, upper = False)

        dat3 = camel_to_space(dat); dat3
        space_to_snake(dat3)
        space_to_camel(dat3)
        space_to_camel(dat3, upper = False)

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    return dataframe.rename(
        columns={
            elem: re.sub(r"([a-z])([A-Z])+", "\g<1> \g<2>", elem)
            for elem in dataframe.columns
        },
        inplace=False,
    )


def snake_to_space(dataframe):
    """Rename DataFrame Columns

    Uses the heuristic current_to_desired case format

    Examples::

        dat = pd.DataFrame({'HelloWorld': [1, 2], 'GoodByeWorld': ['a', 'b']})
        camel_to_snake(dat)
        camel_to_space(dat)

        dat2 = camel_to_snake(dat); dat2
        snake_to_space(dat2)
        snake_to_camel(dat2)
        snake_to_camel(dat2, upper = False)

        dat3 = camel_to_space(dat); dat3
        space_to_snake(dat3)
        space_to_camel(dat3)
        space_to_camel(dat3, upper = False)

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    return dataframe.rename(
        columns={elem: re.sub(r"_+", " ", elem) for elem in dataframe.columns},
        inplace=False,
    )


def space_to_snake(dataframe):
    """Rename DataFrame Columns

    Uses the heuristic current_to_desired case format

    Examples::

        dat = pd.DataFrame({'HelloWorld': [1, 2], 'GoodByeWorld': ['a', 'b']})
        camel_to_snake(dat)
        camel_to_space(dat)

        dat2 = camel_to_snake(dat); dat2
        snake_to_space(dat2)
        snake_to_camel(dat2)
        snake_to_camel(dat2, upper = False)

        dat3 = camel_to_space(dat); dat3
        space_to_snake(dat3)
        space_to_camel(dat3)
        space_to_camel(dat3, upper = False)

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    return dataframe.rename(
        columns={elem: re.sub(r" +", "_", elem).lower() for elem in dataframe.columns},
        inplace=False,
    )


def camel_to_snake(dataframe):
    """Rename DataFrame Columns

    Uses the heuristic current_to_desired case format

    Examples::

        dat = pd.DataFrame({'HelloWorld': [1, 2], 'GoodByeWorld': ['a', 'b']})
        camel_to_snake(dat)
        camel_to_space(dat)

        dat2 = camel_to_snake(dat); dat2
        snake_to_space(dat2)
        snake_to_camel(dat2)
        snake_to_camel(dat2, upper = False)

        dat3 = camel_to_space(dat); dat3
        space_to_snake(dat3)
        space_to_camel(dat3)
        space_to_camel(dat3, upper = False)

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    return dataframe.rename(
        columns={
            elem: re.sub(r"(?<!^)(?=[A-Z])", "_", elem).lower()
            for elem in dataframe.columns
        },
        inplace=False,
    )


## Helper functions
def _to_title(x):
    return pd.Series(x).str.replace(
        "(^|\s+)(?P<letter>[A-z])",
        lambda x: x.group(1) + x.group("letter").upper(),
        regex=True,
    )


def _to_title_camel(x):
    return _to_title(x).str.replace("\\s+", "", regex=True)


def _onedown(x, lower):
    if lower:
        return x[0].lower() + x[1:]
    else:
        return x
