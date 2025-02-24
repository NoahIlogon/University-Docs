import dask.bag as db

'''
When Using Dask remember to protect your code with 

" if __name__ == '__main__': "

which prevents the code from being executed multiple times

This is an example of a Dask Implementation
'''

def main():
    numbers = [1, 2, 3, 4, 5]

    bag = db.from_sequence(numbers, npartitions=2)

    result = bag.map(lambda x: x + 10)

    computed_result = result.compute()

    print(computed_result)

if __name__ == '__main__':
    main()

    