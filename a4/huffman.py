import os
import sys
import marshal
import array
import heapq

try:
    import cPickle as pickle
except:
    import pickle

"""
Function to get the frequency of every letter in the message (frequency table).
Returns the sorted tuple 
"""
def letterFreq(msg):
    # Dictionary to hold the frequency of each letter
    frequency = {}

    # For every single letter in the message
    for letter in msg:
        # If the letter is not in the dictionary, initialize it
        if letter not in frequency:
            frequency[letter] = 0
        # Add the frequency
        frequency[letter] += 1

    heap = []

    # For every single key, value pair in the dictionary, add it to a list of tuples
    for key, value in frequency.items():
        heap.append((value, key))

    # Convert the list into a heap and sort it by the first element in the tuple
    heapq.heapify(heap)
    heap.sort(key=lambda k: k[0])
    return heap


"""
Function to create the tree nodes with the weight and subtree
"""
def wTreeNode(heap):
    while len(heap) > 1:
        # Get the two least frequencies values in the heap
        first, second = heap[0], heap[1]
        # Calculate its weight
        weight = first[0] + second[0]
        # Add the weight and the tuples back to the heap as a subtree (merge)
        heap = heap[2:] + [(weight, (first, second))]
        # Re-sort it
        heap.sort(key=lambda k: k[0])

    return heap

"""
Recursively transform the tree so it does not have the weight:
    wTreeNode = (weight, subtree) --> treeNode = subtree
                                      where subtree = (left, right) | leaf
"""
def treeNode(tree):
    # Ignore the first frequency count
    nodes = tree[1]

    # Check if the nodes are a subtree (left, right)
    if isinstance(nodes, tuple):
        # Get rid of the frequency and recombine the tree
        return (treeNode(nodes[0]), treeNode(nodes[1]))

    # It is a leaf so return it
    return nodes

"""
Recursively creates the dictionary of code values, where the key is the letter and the value is the code
"""
def getCodes(node, codes,  code = ''):
    # Check if its a branch and if it is, add "0" or "1"
    if isinstance(node, tuple):
        # Go to the left
        getCodes(node[0], codes, code + "0")
        # Go to the right
        getCodes(node[1], codes, code + "1")

    else:
        codes[node] = code

"""
Takes a bytes object (a sequence of bytes over which you can iterate), msg 
and returns a tuple (enc, ring) where enc is the ASCII representation of the
Huffman-encoded message (e.g. "1001011") and ring is the "decoder ring"
needed to decompress the message.
"""
def encode(msg):
    # Get a heap containing the frequencies of each letter
    heap = letterFreq(msg)

    # Create a weighted tree
    tree = wTreeNode(heap)

    # Get the tree without the frequencies
    # tree[0] is passed because we only want the single tree
    tree = treeNode(tree[0])

    # Codes is the dictionary containing the characters in the message as the key, and its code as the value
    codes = {}

    # Get the codes of each letter
    getCodes(tree, codes)

    # Opposite of codes dictionary -the key is the code and the value is the character
    decoderRing = {}

    for key, value in codes.items():
        decoderRing[value] = key

    # Will hold the encoded message
    enc = ""

    # Convert every character in the message into its code representation
    for ch in msg:
        enc += codes[ch]

    return (enc, decoderRing)

"""
To decode, we need the tree and the encoded message.
It creates substrings of msg and checks to see if it is in the decoderRing. If it is, it gets the letter and resets.
This function returns a bytes object of the decoded message
"""
def decode(msg, decoderRing):
    # Will hold the decoded message
    dec = array.array('B')

    # Will be used to hold a substring that will be checked to see if is in the decoderRing
    substring = ""

    for i in msg:
        substring += i
        if substring in decoderRing:
            dec.append(decoderRing[substring])
            substring = ""
    return dec


"""
Takes a bytes object, msg, and returns a tuple (compressed, ring) where compressed
is an array of bytes (array.array("B")) containing the Huffman-coded message in binary,
and ring is the "decoder ring" needed to decompress the message.

It is a non-human readable, compressed binary form of a message.
"""
def compress(msg):
    # Initializes an array to hold the compressed message
    compressed = array.array('B')

    # Encode the input text
    enc, decoderRing = encode(msg)

    # Gets how much padding is needed
    padding = (8 - (len(enc) % 8) % 8)

    # Add the padding to the dictionary so that we can use it in decompress
    decoderRing["padding"] = padding

    buf, count = 0, 0

    for bit in enc:
        # Convert the character into a bit
        if bit == '0':
            byteVal = 0x00
        else:
            byteVal = 0x01

        buf = buf | byteVal

        count += 1

        # If there are 9 bits, we have gone over the 8 bit limit and must add that to compressed
        if count == 8:
            compressed.append(buf)
            # Reset the buffer and counter
            buf, count = 0, 0

        # Otherwise, perform a bitwise shift
        else:
            buf = (buf << 1)

    padding -= 1
    
    # If there is padding, we need to add it to the last buf by shifting it
    if padding > 0:
        buf = buf << padding
    compressed.append(buf)

    return compressed, decoderRing

"""
Takes a bitstring (array.array("B") containing the Huffman-coded message in binary,
and the decoder ring needed to decompress it.
It returns the bytes object which is the decompressed message
"""
def decompress(msg, decoderRing):
    # Represent the message as an array
    byteArray = array.array('B', msg)

    # Will hold the bits that need to be decoded
    dec = ""

    # Get the padding from the dictionary
    padding = decoderRing["padding"]

    # Will be used to see if we are at the last value in byteArray (the last byte potentially has padding)
    count = 1
    
    for byte in byteArray:
        # Convert it to binary
        binary = f'{byte:08b}'

        # This is only if not the last -all we have to do is add the binary string to dec
        if count != len(byteArray):
            dec += binary

        # If we are at the last entry in the byteArray, we only get the binary text up until where there is padding
        else:
            dec += binary[:8 - padding]

        count += 1

    # Decode the string and return it
    dec = decode(dec, decoderRing)

    return dec

def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
    if len(sys.argv) != 4:
        usage()
    opt = sys.argv[1]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()

    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        msg = fp.read()
        fp.close()
        if compressing:
            compr, decoder = compress(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(decoder), compr), fcompressed)
            fcompressed.close()
        else:
            enc, decoder = encode(msg)
            print(enc)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(decoder), enc), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pickleRick, compr = marshal.load(fp)
        decoder = pickle.loads(pickleRick)
        fp.close()
        if decompressing:
            msg = decompress(compr, decoder)
        else:
            msg = decode(compr, decoder)
            print(msg)
        fp = open(outfile, 'wb')
        fp.write(msg)
        fp.close()
