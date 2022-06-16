import sys

## useful for getting numbered inputs of a selected list
def menu_input(choices:list, message:str=None):

    if message is None:
        message = 'Choose from the following options:'

    if len(choices) < 2:
        raise Exception('Please provide 2 or more choices')

    lc = len(str(len(choices)))

    print(message + '\n\n' + '\n'.join(['{}: {}'.format('{message:>{width}}'.format(message=str(i + 1), width = lc), j) for i, j in enumerate(choices)]) + '\n', flush = True)
    
    ans = 'Weird start value'
    while ans not in [str(x + 1) for x in range(len(choices))]:
        if ans != 'Weird start value':
            print('Please select a number from the menu above', flush = True)
        ans = input("Selection: ")

    return choices[int(ans) - 1]

## detect the user's operating system
def get_os():

    if sys.platform == 'darwin':
        return 'Mac'
    elif sys.platform.startswith('win') == True:
        return 'Windows'
    elif sys.platform.startswith('linux') == True:
        return 'Linux'
    else:
        return None