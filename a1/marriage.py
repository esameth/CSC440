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

    lines = input_file.readlines()

    # Strip the first line -this should be an int -will be the number of people
    try:
        num_people = int(lines[0])
    except ValueError:
        exit(1)

    # Check the number of lines in the file -this should be 2 * number of people - 1
    if len(lines) != num_people * 2 + 1:
        exit(1)

    input_file.close()
    return num_people, lines[1:]


"""
Reads from a file input and creates the knights and ladies dictionaries.
Knights cannot have the same name as other knights, and ladies cannot have
the same name as other ladies, but a knight and a lady can have the same name -
handled by checking to see if the name is in the dictionary already and
writing to stderr.

@param num_people - to know when to separate the lists
@return knights and ladies dictionaries 
"""
def initiate():
    num_people, lines = file_handling()

    # Create knights and ladies dictionaries that will hold names and preferences
    knights = {}
    ladies = {}

    # Read each line and separate them into name and their preferences
    for i in range(len(lines)):
        line = (lines[i].split('\n', 1)[0]).split(" ")
        name, prefs = line[0], line[1:]

        # Check to see that every person has the right number of preferences
        if len(prefs) != num_people:
            exit(1)

        # Create knight dictionary
        if i < num_people:
            # Put the key and its values in the dictionary
            knights[name] = prefs

        else:
            # Create ladies dictionary
            ladies[name] = prefs

    # Return the dictionaries
    return knights, ladies

"""
Checks to see if the lady prefers another knight over her partner.
@param  knight, engaged, l_pref -the lady and knight we are currently looking at,
                                        the knight she's currently engaged to,
                                        and her preference list
@return True if she does; False if she prefers her current partner more
"""
def check_pref(knight, engaged, l_pref):
    if l_pref.index(engaged) < l_pref.index(knight):
        return False
    return True


"""
Makes sure the marriage is stable
@param  knights, ladies - dictionaries
@return a list of the knight the lady says yes to
"""
def stable(knights, ladies):
    # Dict to hold who the lady is engaged to
    l_partner = {lady:"free" for lady in ladies.keys()}
    # Dict to hold if knight is free
    k_free = {knight:"free" for knight in knights.keys()}

    # While there are free men, continue the algorithm
    while "free" in k_free.values():
        # Get the name of the knight
        knight = list(k_free)[0]
        # Name of the lady we are looking at in his preference list
        lady = knights[knight][0]
        # If the lady is not engaged, engage them
        if l_partner[lady] == "free":
            l_partner[lady] = knight
            # Delete the knight from the free list
            del k_free[knight]
        # If the lady is engaged, see if she prefers him over her current partner
        else:
            # Get who she is currently engaged to
            engaged = l_partner[lady]
            l_pref = ladies[lady]
            # She prefers the knight over her current partner so break them up
            if check_pref(knight, engaged, l_pref):
                k_free[engaged] = "free"
                l_partner[lady] = knight
                del k_free[knight]
            else:
                knights[knight].pop(0)
    return l_partner


def main():
    knights, ladies = initiate()
    partners = stable(knights, ladies)
    for lady, knight in partners.items():
         sys.stdout.write(knight + " " + lady + "\n")

if __name__ == "__main__":
    main()
