"""
Jackson Xie and Elysha Sameth
CSC440: Assignment 1 Perfect Marriage in King Arthur's Court
06 February 2019
"""

import sys

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
    return


"""
Reads from a file input and creates the knights and ladies dictionaries.
Knights cannot have the same name as other knights, and ladies cannot have
the same name as other ladies, but a knight and a lady can have the same name -
handled by checking to see if the name is in the dictionary already and
writing to stderr.

@return knights and ladies dictionaries 
"""


def initiate():
    # Create knights and ladies dictionaries that will hold names and preferences
    knights = {}
    ladies = {}

    # Read the file and strip the first line
    input_file = open(sys.argv[1], "r")
    line = input_file.readline()
    num_people = int(line.strip())

    # Will be used to count how many lines in we are so we can separate knights and ladies evenly
    count = 0
    # Read each line and separate them into knights and ladies
    for line in input_file:
        # Create knight dictionary
        if count < num_people:
            items = line.split()
            key, values = items[0], items[1:]

            # Check to see if the key already exists - knights can't have the same name
            if key in knights:
                sys.stderr.write("Knights cannot have the same name")
                exit(0)

            # Put the key and its values in the dictionary
            knights[key] = values

        # Create ladies dictionary
        else:
            items = line.split()
            key, values = items[0], items[1:]
            if key in ladies:
                sys.stderr.write("Ladies cannot have the same name\n")
                exit(0)

            ladies[key] = values

        count += 1

    input_file.close()

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
    partner_list = list(ladies.get(lady, "none"))
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
    l_partner = []

    # List to hold if knight is free
    k_free = []

    # Fill the lists with "free" initially
    for i in range(len(knights)):
        l_partner.append("free")
        k_free.append("free")

    """ 
        Invariant: At iteration i, there are knights that are not paired with a lady
        Initialization: The list of knights are all free (not paired)
        Maintenance: Given that the num_taken does not equal len(knights) the function will run
                     in attempt to pair the knight with a lady.
        Termination: At the last iteration, the num_taken == len(knights)
    """
    # While there are free men, continue the algorithm
    while num_taken != len(knights):
        i = 0

        """ 
            Invariant: At iteration i, i < len(knights)
            Initialization: i = 0, len(knights) > 0
            Maintenance: Given that the k_free list has indices that aren't "free" the function will continue going
                         until it finds an index that isn't "free" and breaks from the loop
            Termination: At the last iteration, all the indices are "free". When the conditional finds an index
                         that is not free, it will terminate the loop.
        """
        # Get the first knight who is free
        while i < len(knights):
            if k_free[i] == "free":
                break
            else:
                i += 1
        """ 
            Invariant: The list of knights will always be the same size as the k_free
            Initialization: There is a list of knights
            Maintenance: Given that the len(knights) > i
            Termination: When the conditional finds the knight in the index i it will break from the loop
        """
        # Get the name of the knight
        for key in knights:
            if list(knights).index(key) == i:
                knight = key
                break

        """ 
            Invariant: At iteration j, the knights and the k_free previously will no be free.
                       The following ones will be free. 
            Initialization: The knights k_free array has a free index
            Maintenance: Given that k_free[i] is free it will get the index of the lady
                         and check if the lady is free and propose to her. 
            Termination: When there are no longer any knights and k_free[i] is no longer free 
        """
        # Go through all of the free knight's preferences
        j = 0
        while j != len(knights) and k_free[i] == "free":
            # Name of the lady we are looking at in his preference list
            lady = knights.get(knight, "none")[j]

            # Get index of lady
            lady_index = list(ladies).index(lady)

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
                partner_index = list(knights.keys()).index(partner)

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
    file_handling()
    knights, ladies = initiate()
    partners = stable(knights, ladies)

    for key in knights:
        # Find position in partners list to get lady
        lady = partners.index(key)

        # Name of lady
        for name in ladies:
            if list(ladies).index(name) == lady:
                lady = name
                break

        sys.stdout.write(key + " " + lady + "\n")


if __name__ == "__main__":
    main()
