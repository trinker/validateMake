def make_batch(length: int, batch_size: int):
    """
    Create Indices for Braking a Structure into Batches

    Parameters:
        length: The length (or rows) of the object you want to break into batches
        batch_size:  The number of items (or rows) you want in each batch

    Examples::

        import pandas as pd
        import numpy as np
        data = pd.DataFrame({
            'id' : [i + 1 for i in range(125)],
            'x': np.random.normal(100, 10, 125),
            'y': np.random.normal(12, 3, 125)
        })


        batched_i = make_batch(length = data.shape[0], batch_size = 50)
        list_tuples = list(batched_i)
        ## Note that wrapping list() around zip makes it point to empty list after it's done iterating
        ## list(batched_i)
        list_tuples
        pd.DataFrame(list_tuples, columns = ['Start', 'End', 'i'])

        ## Use it to make a list of batched dataframes
        [data.iloc[s:e].copy() for s, e, i in make_batch(length = data.shape[0], batch_size = 50)]

        ## Use it to make a list of batched dataframes
        [data.iloc[s:e].copy() for s, e, i in make_batch(length = data.shape[0], batch_size = 25)]

        ## Break a list into batches
        id = [i + 1 for i in range(125)]
        new_dict = {i + 1: id[s:e] for s, e, i in make_batch(length = len(id), batch_size = 40)}
        for k, v in new_dict.items():
            # no need to escape the slash if copying directly from the docstring
            print('\\n=============\\n' + str(k))
            print(v)
    """
    starts = [x for x in list(range(0, length, batch_size))]
    ends = list(range(batch_size, length, batch_size)) + [length]
    return zip(starts, ends, list(range(len(starts))))
