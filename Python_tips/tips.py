def main():

    """use pathlib for Python >= 3.4"""
    from pathlib import Path

    directory = Path('main_dir', 'sub_dir')
    file = 'example.json'

    print(Path(directory, file))
    # >>> "main_dir/sub_dir/example.json"

    """use os for Python < 3.4"""
    import os

    directory = os.path.join('main_dir', 'sub_dir')
    file = 'example.json'

    print(os.path.join(directory, file))
    # >>> "main_dir/sub_dir/example.json"

    """variable unpacking"""

    name, age, job = ['Pietje Puk', 27, 'Data Scientist']  # unpack lists & tuples

    a, b, c = '123'  # unpack strings
    # >>> a
    # '1'

    a, b, c = (i**2 for i in range(2, 5))  # unpack generator
    # >>> a
    # 4

    person = {'name': 'Pietje Puk', 'age': 27, 'profession': 'Data Scientist'}

    a, b, c = person  # unpacking dictionary keys
    # >>> a
    # 'name'

    a, b, c = person.values()  # unpacking dictionary values
    # >>> b
    # 27

    a, b, c = person.items()  # unpacking (key-value pairs)
    # >>> a
    # ('name', 'Pietje Puk')  # a tuple

    """keyword arguments"""
    persons = [
        {'first_name': 'Louis', 'last_name': 'de Bruijn', 'age': 26, 'profession': 'Data Scientist'},
        {'first_name': 'Pietje', 'last_name': 'Puk', 'age': 18, 'profession': 'student'},
    ]

    for cnt, person in enumerate(persons):
        print("Person {0}'s occupation is {profession}.".format(cnt, **person))
    # >>> Person 0's occupation is Data Scientist.
    # >>> Person 1's occupation is student.

    """data comprehensions"""
    # lists and tuples: [element for element in iterator]
    elements = []
    for i in range(1, 6):
        elements.append(i)

    elements = [i for i in range(1, 6)]
    # >>> elements
    # [1, 2, 3, 4, 5]

    # dictionaries: {key: value for element in iterator}
    alphabet = 'abcde'

    dictionary = {}
    for i in range(1, 6):
        dictionary[i] = alphabet[i]

    dictionary = {i: alphabet[i] for i in range(1, 6)}
    # >>> dictionary
    # {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}

    """zip functions"""

    list1 = [102, 306, 918, 2754]
    list2 = [1, 3, 9, 27]

    averages = []
    for idx1, el1 in enumerate(list1):  # first for-loop
        for idx2, el2 in enumerate(list2):  # second for-loop
            if idx1 == idx2:  # check whether the indexes of first * second for-loop match
                y_intercept = el1 / el2
                averages.append(y_intercept)
    # >>> averages
    # [102.0, 102.0, 102.0, 102.0]

    averages = []
    for el1, el2 in zip(list1, list2):  # loop through both list using zip
        y_intercept = el1 / el2
        averages.append(y_intercept)
    # >>> averages
    # [102.0, 102.0, 102.0, 102.0]

    """asterisk operators"""

    # Example 1: shuffle data to ensure random class distribution in train/test split
    import random

    documents = ['positive tweet message', 'negative tweet message']
    labels = ['pos', 'neg']

    tuples = [(doc, label) for doc, label in zip(documents, labels)]
    random.shuffle(tuples)
    X, Y = zip(*tuples)

    # Example 2: merging two dictionaries
    first_dictionary = {'A': 1, 'B': 2}
    second_dictionary = {'C': 3, 'D': 4}
    {**first_dictionary, **second_dictionary}

    # >>> merged_dictionary
    # {"A": 1, "B": 2, "C": 3, "D": 4}

    # Example 3: dropping unneccesary function variables
    def return_stuff():
        """Example function that returns data."""
        return 'This', 'is', 'interesting', 'This', 'is', 'not'

    a, b, c, *_ = return_stuff()


if __name__ == '__main__':
    main()
