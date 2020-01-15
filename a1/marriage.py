import sys
from itertools import islice
import numpy as np

"""
All of the exception handling for the file format.
It will check that there are enough arguments, a valid input file, that the first line is an int,
there are enough lines, and that there are enough names in each line.
It will exit(1) if any of these conditions are not true
"""
def file_handling():
    # Check to see if there are enough arguments provided
    if len(sys.argv) != 2:
        exit(1)

    # Open input file from the command line
    try:
        input_file = open(sys.argv[1], "r")
    except IOError:
        exit(1)

    line = input_file.readline()

    # Strip the first line -this should be an int -will be the number of people
    try:
        num_people = int(line.strip())
    except ValueError:
        exit(1)

    # Used to count the number of lines in the file -this should be 2 * number of people - 1
    num_lines = 0
    for line in input_file:
        num_lines += 1

        items = line.split()

        # Count number of people in each line to see if the person has the right number of preferences
        if len(items) != num_people + 1:
            exit(1)

    if num_lines != num_people * 2:
        exit(1)

    input_file.close()
    return num_people

"""
Reads from a file input and creates the knights and ladies dictionaries.
Knights cannot have the same name as other knights, and ladies cannot have
the same name as other ladies, but a knight and a lady can have the same name -
handled by checking to see if the name is in the dictionary already and
writing to stderr.

@param num_people - to know when to separate the lists
@return knights and ladies dictionaries 
"""
def initiate(num_people):
    # Create knights and ladies dictionaries that will hold names and preferences
    knights = {}
    ladies = {}

    with open(sys.argv[1], 'r') as input_file:
        # Will be used to count how many lines in we are so we can separate knights and ladies evenly
        count = 0
        # Read each line and separate them into knights and ladies
        # Skip the first line because it is the number of people
        for line in islice(input_file, 1, None):
            items = line.split()
            key, values = items[0], items[1:]

            # Create knight dictionary
            if count < num_people:
                # Check to see if the key already exists - knights can't have the same name
                if key in knights:
                    sys.stderr.write("Knights cannot have the same name")
                    exit(0)
                # Put the key and its values in the dictionary
                knights[key] = values

            # Create ladies dictionary
            else:
                if key in ladies:
                    sys.stderr.write("Ladies cannot have the same name\n")
                    exit(0)
                ladies[key] = values
            count += 1
    # Return the dictionaries
    return knights, ladies

"""
Checks to see if the lady prefers another knight over her partner.
@param  knights, ladies - dictionaries
        lady, knight, partner -the lady and knight we are currently looking at 
                                and the knight she's currently engaged to
@return True if she does; False if she prefers her current partner more
"""
def l_pref(ladies, lady, knight, partner):
    partner_list = ladies[lady]
    partner_index = partner_list.index(partner)
    knight_index = partner_list.index(knight)
    if partner_index < knight_index:
        return False

    return True

"""
Makes sure the marriage is stable
@param  knights, ladies - dictionaries
@return a list of the knight the lady says yes to
"""
def stable(knights, ladies):
    # Count the number of couples
    num_taken = 0
    # List to hold who the lady is engaged to
    l_partner = ["free"] * len(knights)
    # List to hold if knight is free
    k_free = ["free"] * len(knights)

    knightList = list(knights)
    ladiesList = list(ladies)

    # While there are free men, continue the algorithm
    while num_taken != len(knights):
        # Get the first knight who is free
        i = k_free.index("free")
        # Get the name of the knight
        knight = knightList[i]

        # Go through all of the free knight's preferences
        j = 0
        while j != len(knights) and k_free[i] == "free":
            # Name of the lady we are looking at in his preference list
            lady = knights[knight][j]

            # Get index of lady
            lady_index = ladiesList.index(lady)

            # If the lady is free then the knight will propose to her
            if l_partner[lady_index] == "free":
                l_partner[lady_index] = knight
                k_free[i] = "taken"
                num_taken += 1

            # The lady is already taken but they may become partners if the lady prefers him over her partner
            else:
                # Get name of the knight engaged to the lady
                partner = l_partner[lady_index]
                # Get partner index in case we have to set him to "free"
                partner_index = knightList.index(partner)

                # If the lady does prefer the knight over her current fiance, break them up
                if l_pref(ladies, lady, knight, partner):
                    # The lady is now engaged to the knight
                    l_partner[lady_index] = knight
                    # The knight is now taken while her ex-fiance is free
                    k_free[i] = "taken"
                    k_free[partner_index] = "free"

            j += 1
    return l_partner

def main():
    num_people = file_handling()
    knights, ladies = initiate(num_people)
    partners = stable(knights, ladies)

    for knight in knights:
        # Find position in partners list to get lady
        lady = partners.index(knight)
        lady = list(ladies)[lady]
        sys.stdout.write(knight + " " + lady + "\n")

if __name__ == "__main__":
    main()
