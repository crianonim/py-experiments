import csv
import string
import random
import uuid


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


filename = 'data/ids10M.csv'


def main():
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for i in range(10000000):
            csvwriter.writerow([i, uuid.uuid4(), id_generator()])


def testRead():
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for _ in reader:
            pass


if __name__ == "__main__":
    main()
