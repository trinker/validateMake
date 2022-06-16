import pandas as pd


def title_case(x):
    """Convert a List/Pandas Series to Title (Headline) Case

    Parameters:
        x: A list or Pandas Series

    Examples::

        x = ["I see to see him go After him", 'the farmer and the dell']
        title_case(x)
    """
    x = pd.Series(x)
    x = x.str.title()
    return x.str.replace(
        "(?<=\\s)(A|An|And|Are|As|At|Be|But|By|En|For|If|In|Is|Nor|Not|Of|On|Or|Per|So|The|To|V[.]?|Via|Vs[.]?|From|Into|Than|That|With)\\b",
        lambda z: z.group(1)[0].lower() + z.group(1)[1:],
        regex=True,
    )
