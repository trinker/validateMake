import pandas as pd
import numpy as np
import re
import warnings


class Sub:

    """Replace Common Text Strings

    Examples::

        import pandas as pd
        from ds.clean import Sub

        pd.set_option('display.max_colwidth', 10000)

        sub = Sub()

        dat = pd.DataFrame({'text': ["@hadley I like #rstats for #ggplot2 work. ftp://cran.r-project.org/incoming/",
            "Difference between #magrittr and #pipeR, both implement pipeline operators for #rstats: ",
            " http://renkun.me/r/2014/07/26/difference-between-magrittr-and-pipeR.html @timelyportfolio end",
            "Slides from great talk: @ramnath_vaidya: Interactive slides from Interactive Visualization",
            "presentation #user2014. https://ramnathv.github.io/user2014-rcharts/#1",
            None,
            "<bold>Random</bold> text with symbols: &nbsp; &lt; &gt; &amp; &quot; &apos;",
            "<p>More text</p> &cent; &pound; &yen; &euro; &copy; &reg; &laquo; &raquo;",
            "fred is fred@foo.com and joe is joe@example.com - but @this is a",
            "twitter handle for twit@here.com or foo+bar@google.com/fred@foo.fnord",
        ]})


        dat['cleaned'] = sub.all(dat.text)
        dat['cleaned']
        sub.url(dat.text)
        sub.html(dat.text)
        sub.hash(dat.text)
        sub.mention(dat.text)
        sub.email(dat.text)

        sub.email(dat.text, '<a href="mailto:\\1" target="_blank">\\1</a>')

        ## -OR-

        ## Replacement with function (same as previous)
        def email_repl(match):
            return '<a href="mailto:{}" target="_blank">{}</a>'.format(match.group(), match.group())

        sub.email(dat.text, email_repl)

        ## -OR-

        ## Replacement with lambda (same as previous)...note use of match and match.group()?
        sub.email(dat.text, lambda match: '<a href="mailto:{}" target="_blank">{}</a>'.format(match.group(), match.group()))

        ## lambda replacement
        sub.hash(dat.text, lambda match: '{{' + match.group()[::-1] + '}}')

        dir(sub)
    """

    def __init__(self):
        self.regex = {
            "hash": "((?<!/)((?:#)(?:\\w+)))",
            "mention": "((?<![@\\w])@([A-z0-9_.]+))",
            "url": "((?:https?|ftp|www\\.)[^ ]*)",
            "html_tag": "(<[^>]*>)",
            "email": "([_+A-z0-9-]+(?:\\.[_+A-z0-9-]+)*@[A-z0-9-]+(?:\\.[A-z0-9-]+)*(?:\\.[A-z]{2,14}))",
        }

        self.dict_replace_regex = {"html_escape": _html_escapes}

    def url(self, x, repl: str = ""):
        """Replace URL"""
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")
        return _replace_regex(input, self.regex.get("url"), repl)

    def email(self, x, repl: str = ""):
        """Replace Email Addresses"""
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")
        return _replace_regex(input, self.regex.get("email"), repl)

    def html_tag(self, x, repl: str = ""):
        """Replace HTML Tags"""
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")
        return _replace_regex(input, self.regex.get("html_tag"), repl)

    def html_escape(self, x):
        """Replace HTML Escapes"""
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")
        return _replace_dict(input, self.dict_replace_regex.get("html_escape"))

    def html(self, x, repl: str = "", replace_escapes: bool = True):
        """Replace HTML escapes and tags"""
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")
        if replace_escapes:
            input = _replace_dict(input, self.dict_replace_regex.get("html_escape"))
        return _replace_regex(input, self.regex.get("html_tag"), repl)

    def mention(self, x, repl: str = ""):
        """Replace twitter style @ handles"""
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")
        return _replace_regex(input, self.regex.get("mention"), repl)

    def hash(self, x, repl: str = ""):
        """Replace twitter style hash tags"""
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")
        return _replace_regex(input, self.regex.get("hash"), repl)

    def all(self, x, repl: str = ""):
        """Applies all available replacement methods"""
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")
        input = _replace_regex(input, self.regex.get("hash"), repl)
        input = _replace_regex(input, self.regex.get("mention"), repl)
        input = _replace_regex(input, self.regex.get("url"), repl)
        input = _replace_dict(input, self.dict_replace_regex.get("html_escape"))
        input = _replace_regex(input, self.regex.get("html_tag"), repl)
        input = _replace_regex(input, self.regex.get("email"), repl)
        return input

    def update_regex(self, key, regex):
        """Update the regexes in the underlying regex dictionary attribute"""
        reg = self.regex
        if reg.get(key) is None:
            raise Exception("'{}' is not a `key` in the regex dictionary".format(key))

        reg[key] = _check_regex(regex)
        setattr(self, "regex", reg)

    def fun(self, x, pattern, fun, ignore_case=False):

        """Replace a regex pattern with an Functional Operation on the Regex Match

        Finds a regex match, and then uses a function to operate on these matches
        and uses the return values to replace the original matches.

        Parmeters:
            x: A string list/pd.Series
            pattern: String to be matched in the given character vector
            fun: A function to operate on the extracted matches
            ignore_case: Should case be ignore

        Examples::

            from ds.clean import Sub

            pd.set_option('display.max_colwidth', 10000)

            sub = Sub()

            txt = [None, 'I want 32 grapes', 'he wants 4 ice creams', 'they want 1,234,567 dollars']

            ## packages for function below
            import re
            import math

            ## Note that the argument to the function is `match` and inside we use `match.group()`
            def number_half(match):
                return '{:,}'.format(math.ceil(int(re.sub('[^0-9]', '', match.group()))/2))

            sub.fun(txt, '[\\d,]+', number_half)

            sub.fun(txt, '[\\d,]+', lambda match: '{:,}'.format(math.ceil(int(re.sub('[^0-9]', '', match.group()))/2)))
        """
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")

        if ignore_case:
            case_flag = re.IGNORECASE
        else:
            case_flag = 0

        return input.str.replace(
            _check_regex(pattern), fun, regex=True, flags=case_flag
        )

    def many(
        self,
        x,
        regex_dict,
        ignore_case: bool = None,
        regex: bool = False,
        order_pattern: bool = None,
    ):

        """Multiple Replacements

        Parameters:
            x: A string list/pd.Series
            regex_dict: A dictionary where the keys are the patterns and the values are the replacements
            ignore_case: Should case be ignore?  If None then is set to `regex`'s value
            regex: Determines if the passed-in pattern is a regular expression: If True, assumes the passed-in pattern is a regular expression. If False, treats the pattern as a literal string
            order_pattern: If True and regex = False, the dictionary is sorted by number of characters in the keys to prevent substrings replacing meta strings (e.g., keys = ["the", "then"] resorts to search for "then" first)

        Examples::

            from ds.clean import Sub

            pd.set_option('display.max_colwidth', 10000)

            sub = Sub()

            regex_dict = {
                "there": "truck",
                "the": "then",
                "world": "hello"
            }

            x = ["Hello World", "Pin backpack block!", "I see the dog over there the2"]
            sub.many(x, regex_dict, regex = False) ## ignore_case defaults to False
            sub.many(x, regex_dict, regex = True) ## ignore_case defaults to True
            sub.many(x, regex_dict, regex = False, ignore_case = True)
            sub.many(x, regex_dict, regex = False, ignore_case = False)

            regex_dict2 = {
                "the[A-z]+": "truck",
                "[oa]ck": "am",
                "[Ww]orld": "hello",
                "I": "<(o)>"
            }
            sub.many(x, regex_dict2, regex = True, ignore_case = True)
            sub.many(x, regex_dict2, regex = True, ignore_case = False)
        """

        if ignore_case is None:
            ignore_case = regex

        if ignore_case:
            case_flag = re.IGNORECASE
        else:
            case_flag = 0

        input = pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore")

        [_check_regex(k) for k in regex_dict.keys()]

        ## --TO DO--Note that there is no safe substitution like there is in textclean::mgsub()
        ## https://mran.microsoft.com/snapshot/2020-09-11/web/packages/mgsub/vignettes/Safe-Substitution.html
        ## if (safe) {
        ##     return(mgsub_regex_safe(x = x, pattern = pattern, replacement = replacement, ...))
        ## }

        if (not regex) and order_pattern:
            ord = np.argsort([len(k) for k in regex_dict.keys()])[::-1]
            regex_dict = {
                list(regex_dict.keys())[i]: list(regex_dict.values())[i] for i in ord
            }

        for k, v in regex_dict.items():
            input = input.str.replace(k, v, regex=regex, flags=case_flag)

        return input

    def many_fixed(
        self,
        x,
        regex_dict,
        ignore_case: bool = False,
        regex: bool = False,
        order_pattern: bool = None,
    ):

        """Multiple Replacements Fixed

        A wrapper for many() that assumes that `regex = False` and `ignore_case = True`

        Parameters:
            x: A string list/pd.Series
            regex_dict: A dictionary where the keys are the patterns and the values are the replacements
            ignore_case: Should case be ignore
            regex: Determines if the passed-in pattern is a regular expression: If True, assumes the passed-in pattern is a regular expression. If False, treats the pattern as a literal string
            order_pattern: If True and regex = False, the pattern string is sorted by number of characters to prevent substrings replacing meta strings (e.g., pattern = c("the", "then") resorts to search for "then" first).

        Examples::

            from ds.clean import Sub

            pd.set_option('display.max_colwidth', 10000)

            sub = Sub()

            regex_dict = {
                "there": "truck",
                "the": "then",
                "world": "hello"
            }

            x = ["Hello World", "Pin backpack block!", "I see the dog over there the2"]
            sub.many_fixed(x, regex_dict)
            sub.many_fixed(x, regex_dict, ignore_case = True)
        """
        return self.many(x, regex_dict, ignore_case, regex, order_pattern)

    def many_regex(
        self,
        x,
        regex_dict,
        ignore_case: bool = True,
        regex: bool = True,
        order_pattern: bool = None,
    ):

        """Multiple Replacements Regex

        A wrapper for many() that assumes that `regex = True` and `ignore_case = False`

        Parameters:
            x: A string list/pd.Series
            regex_dict: A dictionary where the keys are the patterns and the values are the replacements
            ignore_case: Should case be ignore
            regex: Determines if the passed-in pattern is a regular expression: If True, assumes the passed-in pattern is a regular expression. If False, treats the pattern as a literal string
            order_pattern: If True and regex = False, the pattern string is sorted by number of characters to prevent substrings replacing meta strings (e.g., pattern = c("the", "then") resorts to search for "then" first).

        Examples::

            from ds.clean import Sub

            pd.set_option('display.max_colwidth', 10000)

            sub = Sub()

            regex_dict = {
                "the[A-z]+": "truck",
                "[oa]ck": "am",
                "[Ww]orld": "hello",
                "I": "<(o)>"
            }

            x = ["Hello World", "Pin backpack block!", "I see the dog over there the2"]
            sub.many_regex(x, regex_dict)
            sub.many_regex(x, regex_dict, ignore_case = False)

        """
        return self.many(x, regex_dict, ignore_case, regex, order_pattern)


## Helper functions
def _replace_regex(input, pat, repl: str = ""):
    return input.str.replace(pat, repl, regex=True)


def _replace_dict(input, dict: dict):

    for old, new in dict.items():
        input = input.str.replace(old, new, regex=False)

    return input


def _check_regex(x):

    try:
        re.compile(x)
        is_valid = True
    except re.error:
        is_valid = False

    if not is_valid:
        raise Exception("'{}' is not a valid `regex`".format(x))

    return x


## Regex Sub/Repl Dictionaries
_html_escapes = {
    "&copy;": "(c)",
    "&reg;": "(r)",
    "&trade;": "tm",
    "&ldquo;": """,
	"&rdquo;": """,
    "&lsquo;": "'",
    "&rsquo;": "'",
    "&bull;": "-",
    "&middot;": "-",
    "&sdot;": "[]",
    "&ndash;": "-",
    "&mdash;": "-",
    "&cent;": "cents",
    "&#162;": "cents",
    "&pound;": "pounds",
    "&#163;": "pounds",
    "&euro;": "euro",
    "&ne;": "!=",
    "&frac12;": "half",
    "&frac14;": "quarter",
    "&frac34;": "three fourths",
    "&deg;": "degrees",
    "&larr;": "<-",
    "&rarr;": "->",
    "&hellip;": "...",
    "&nbsp;": " ",
    "&lt;": "<",
    "&gt;": ">",
    "&laquo;": "<<",
    "&raquo;": ">>",
    "&amp;": "&",
    "&quot;": '"',
    "&apos;": "'",
    "&yen;": "yen",
    "&#133;": "...",
    "&#149;": "-",
    "&#151;": "---",
    "&#150;": "--",
    "&#153;": "trademark",
    "&#153;": "trademark",
    "&trade;": "+/-",
}
