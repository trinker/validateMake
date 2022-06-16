import re
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF


def camel_to_snake(dataframe):
    """Rename DataFrame Columns

    Uses the heuristic current_to_desired case format

    Examples:

    .. code-block:: python
    
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
        raise Exception('`dataframe` does not appear to be a Pandas DataFrame')
    
    return dataframe.rename(columns= {elem: re.sub(r'(?<!^)(?=[A-Z])', '_', elem).lower() for elem in dataframe.columns}, inplace=False)



def percentile(x):
    """Break Floats into Percentiles
        
    A wrapper for statsmodels' `ECDF` that is used to break a list or pandas Series into percentiles
    
    Parameters:

        x: A numeric list or pandas Series.
    
    Returns: Returns the percentile for each element.

    Examples:

    .. code-block:: python

        import matplotlib.pyplot as plt
        import numpy as np
        from sneetches import percentile

        data = np.random.normal(0,5, size=2000)
        plt.hist(data)
        plt.show()

        plt.hist(percentile(data))
        plt.show()

    """
    return ECDF(x)(x)
