"""
BlockChain Cryptocurrency
Unessay Final Project
CPSC 329 - Fall 2020

Group members:
    Owen Hunter
    Syed Ahmed
    Markus Pistner
    Logan Perry-Din


View README to see instructions

Code below was written using a number of sources as a rough guide:

https://3583bytesready.net/2016/09/06/hash-puzzes-proofs-work-bitcoin/ 
https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b
https://medium.com/coinmonks/python-tutorial-build-a-blockchain-713c706f6531
https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
https://developer.ibm.com/technologies/blockchain/tutorials/develop-a-blockchain-application-from-scratch-in-python/
https://www.youtube.com/watch?v=bBC-nXj3Ng4
https://www.smashingmagazine.com/2020/02/cryptocurrency-blockchain-node-js/ 
"""

from hashlib import sha256
import json
import time
import os
import glob
import datetime as date


"""
Block: a block in the block chain.
    contains an index, list of transactions, timestamp for its creation
    the hash of the previous block and the nonce used to calculate its hash.

When a new block is mined, a json file called 'block_i.json" will be created
where i is the blocks index, and all data is stored inside the block.
"""
class Block:
    def __init__(self, index, transactions, timeStamp, prev_hash):
        self.index = index
        self.transactions = transactions
        self.timeStamp = timeStamp
        self.prev_hash = prev_hash

        # nonce is initialized to zero, only incrememted when computing hash
        self.nonce = 0


        # create a json object that contains all the fields of the block
        # https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
        json_obj = json.dumps(self.__dict__, indent=4, sort_keys=True)

        file_name = "block_" + str(self.index) + ".json"
        with open(file_name, "w") as outfile:
            outfile.write(json_obj)


    # returns the computed SHA256 hash of the blocks json object
    def get_hash(self):
        dump = json.dumps(self.__dict__, indent=4, sort_keys=True)
        return sha256(dump.encode()).hexdigest()


"""
Block_chain: chain of blocks

Creates a genesis block upon creation of the chain
Keeps track of latest block
Computes valid hashes according to the proof of work and
    adds them to the chain
"""
class Block_chain:
    # difficulty of proof of work algorithm
    # number of leading zeroes in the hash
    difficulty_level = 5

    # on creation, create empty lists for unconfirmed transactions and chain
    # and create the genesis block
    def __init__(self):
        self.unconfirmedTransactions = []
        self.chain = []
        self.create_origin_block()


    """
    creates genesis block with default and empty values
    then appends it to the chain.

    hash will not be computed using previous hash (since there is none)
    and will not go through the proof of work

    params: none, returns: none
    """
    def create_origin_block(self):
        origin_block = Block(0, [], time.time(), "0")
        origin_block.hash = origin_block.get_hash()
        self.chain.append(origin_block)



    """
    add_block: adds a block to the chain, if it is valid
        a valid block will match the previous hash of the last block
        and have a valid proof of work

    Params:
        block: block object to add
        proof: hash that conforms to proof of work rules

    Returns:
        bool: True if the block was valid and added, false otherwise
    """
    def add_block(self, block, proof):

        # actual previous hash of the last block
        last_block_hash = self.last_block.hash

        # if the previous hash of the input block doesn't match the actual previous hash
        # return false and don't add the block
        if last_block_hash != block.prev_hash:
            print("\nHash is not equal to previous hash!! Rejecting fraduluent block!\n")
            # delete the invalid blocks json file
            file_name = "block_" + str(block.index) + ".json"
            os.remove(file_name)
            return False

        # if the proof of work is not valid, return false and don't add it
        if not self.check_proof_validity(block, proof):
            print("\nHash did not satisfy proof of work!! Rejecting fraduluent block!\n")
            # delete the invalid blocks json file
            file_name = "block_" + str(block.index) + ".json"
            os.remove(file_name)
            return False

        # the proof of work is valid, add the block and return true
        block.hash = proof
        self.chain.append(block)
        return True

    """
    append a transaction to unconfirmed pool
    """
    def add_new_transaction(self, transaction):
        self.unconfirmedTransactions.append(transaction)


    """
    proof_of_work: computes a hash with difference nonce values until hash satisfies criteria
        uses brute force to increment nonce until hash is found

    params: block: block to compute hash of
    returns: hash_calculated: string of hash that was computed
    """
    def proof_of_work(self, block):

        # while the hash does not begin with difficulty number of 0's
        # increment the block's nonce and calculate the hash again
        hash_calculated = block.get_hash()
        while not hash_calculated.startswith('0' * Block_chain.difficulty_level):
            block.nonce += 1
            hash_calculated = block.get_hash()

        return hash_calculated



    """
    check_proof_validity: checks if the computed hash starts with the right amount of zeroes
        and is the same hash as the one of the block
    """
    def check_proof_validity(self, block, block_hash):
        return (block_hash.startswith('0' * Block_chain.difficulty_level) and block_hash == block.get_hash())




    """
    mine: mines a new block containing all unconfirmed transactions

    params: none
    returns:
        false: if there are no pending transactions and thus no blocks to add
        new_block.index: index of the newly added block
    """
    def mine(self):

        # if no transactions / blocks to mine
        if not self.unconfirmedTransactions:
            return False

        last_block = self.last_block

        ##########################################
        # change one of these two functions to create invalid blocks

        # create a new block with all pending transactions
        new_block = Block(last_block.index + 1, self.unconfirmedTransactions, time.time(), last_block.hash)
        # create a block but the previous hash is not correct
        #new_block = Block(last_block.index + 1, self.unconfirmedTransactions, time.time(), "invalid hash")

        # perform the proof of work
        proof = self.proof_of_work(new_block)
        # don't perform the proof of work
        #proof = "invalid proof"

        ##########################################

        # attempt to add the block to the chain with the newly computed proof of work
        if not self.add_block(new_block, proof):
            return False

        # reset transaction pool
        self.unconfirmedTransactions = []
        return new_block.index

    # property for getter of most recent block
    # https://www.geeksforgeeks.org/getter-and-setter-in-python/
    @property
    def last_block(self):
        return self.chain[-1]



####################################################################################################
#                                   end of classes code                                            #
#                                   beginning of interfaces                                        #
####################################################################################################

"""
Wallet: function to compute money in the chain, for a given name
Shows total money that the user has, and history of transactions
"""
def wallet():

    # list of all json files i.e. all blocks
    files = [f for f in glob.glob("*.json")]

    if len(files) == 1:
        print("\nNo blocks created yet!\n")
        return

    name = input("\nEnter your name: ")
    inp = "cpsc329"

    while(inp != "exit"):
        print("------------------------------")
        print("         "+ name +"'s Wallet     ")
        print("------------------------------")
        print("|| history || total || exit ||")
        print("------------------------------")
        inp = input("\nEnter Command: ")

        total = 0
        num = 0

        if(inp == "history"):
    # for every json file
            for f in files:

        # get block number, index of char in file name
                i = f[6]

        # open the json file
                file_name = "block_" + i + ".json"
                fopen = open(file_name,)
                data = json.load(fopen)

        # for every transaction in the json file
        # look in "transactions" field of json file
                for trans in data["transactions"]:

            # if the input name matches this transaction
                    if (name in trans):
                        #if user sent the money make amount negative and
                        #print appropriate message
                        if(name == trans[0]):
                            amnt = int(trans[2])
                            print("Match! Sent " + str(amnt) + " to " + trans[1])
                            amnt = amnt * -1
                            total+= amnt
                            num = num + 1
                        #if user recieved the money then keep ammount positve
                        #and print appropriate message
                        else:
                            amnt = int(trans[2])
                            total+= amnt
                            num = num + 1
                            print("Match! Recieved " + str(amnt) + " from " + trans[0])

            #If no transactions matching name were found tell user
            if(num == 0):
                print("No block with " + name + " was found..")

            con = input("\nPress enter to continue: ")

        elif(inp == "total"):
            for f in files:

             # get block number, index of char in file name
                i = f[6]

             # open the json file
                file_name = "block_" + i + ".json"
                fopen = open(file_name,)
                data = json.load(fopen)

             # for every transaction in the json file
             # look in "transactions" field of json file
                for trans in data["transactions"]:

                 # if the input name matches this transaction
                 if (name in trans):
                     #if user sent the money make ammount negative
                        if(name == trans[0]):
                             amnt = int(trans[2])
                             amnt = amnt * -1
                             total+= amnt
                     #if the user recieved the money keep amount positve
                        else:
                             amnt = int(trans[2])
                             total+= amnt

            #print out total from all of user's tranactions
            print("Total money for " + name + " is " + str(total) + "$")
            if(total < 0):
                print("Uh oh looks like " + name + " is in debt")
            con = input("\nPress enter to continue: ")

        #For exiting the the loop
        elif(inp == "exit"):
            continue

        else:
            print("Invalid Command")


"""
 delete all pre-existing json files
 done at setup to initialize a new chain
 https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
"""
def rm_json():

    cwd = os.getcwd()
    dir_json = cwd + "/*.json"

    files = glob.glob(dir_json)

    for f in files:
        os.remove(f)


# prints a big string
def show_commands():
    print("\nEnter \"buy\" to make a transaction" + \
    "\nEnter \"mine\" to mine a new block, containing your just entered transactions" + \
    "\nEnter \"show\" to show the details of the most recent block" + \
    "\nEnter \"wallet\" to view the money in the chain" + \
    "\n\nEnter \"exit\" to exit" + \
    "\nEnter \"help\" to show these commands\n")


"""
main function:
    creates an empty chain and interacts with user to add blocks
"""
def main():

    # delete all pre-existing json files
    # may want to change this
    rm_json()

    # initialize a new blockchain object
    chain = Block_chain()

    show_commands()

    inp = ""
    while (inp != "exit"):
        print("\n\n---------------------------------------------------")
        print("||                 MAIN MENU                     ||")
        print("---------------------------------------------------")
        print("|| buy || mine || show || wallet || exit || help ||")
        print("---------------------------------------------------\n")
        inp = input("\nEnter Command: ")


        # if input is "buy", enter transaction menu
        if (inp == "buy"):
            print("\nFormat for Transactions, separated with spaces: from(str), to(str), amount(int)")
            print("eg: Enter transaction: John Bob 5\n")

            # process transaction as string with three values, separated by spaces
            trans_inp = input("Enter your transaction: ")
            trans = trans_inp.split()


            if (len(trans) != 3):
                print("invalid transaction")
            elif(trans[2].isdigit() == False):
                print("invalid transaction enter an integer for amount")
            elif(trans[0] == trans[1]):
                print("Cannot transfer money to yourself")
            else:
                print("Your transaction: " + \
                "   \nfrom: " + trans[0] + ", to: " + trans[1] + ", amount: " + trans[2])


                # confirm or cancel transaction
                conf = input("\nConfirm transaction (y/n): ")
                if(conf == "y"):
                    chain.add_new_transaction(trans)
                if (conf == "n"):
                    print("Transaction discarded.. returning to main menu")
                if(conf != "y" and conf != "n"):
                    print("Please enter y or n")


        # if input is "mine", call mine function
        # program will mine a new block and user will have to wait
        elif (inp == "mine"):
            if chain.mine():
                print("Mining new block with difficulty of " + str(chain.difficulty_level) + " ...")
                print("Mining successful! New block added to chain")
            else:
                print("No blocks to mine! make a transaction to create a block..")

         #if input is "show", print the last block and all of its fields
        elif (inp == "show"):
            print("Last block:" + \
            "\n Index: " + str(chain.last_block.index) + \
            "\n Transactions: " + str(chain.last_block.transactions) + \
            "\n timeStamp: " + str(chain.last_block.timeStamp) + \
            "\n Previous Hash: " + str(chain.last_block.prev_hash) + \
            "\n This Block Hash: " + str(chain.last_block.hash) + \
            "\n Nonce: " + str(chain.last_block.nonce))

        #add elif to avoid else case, can change loop to while(true) and change continue to break;
        elif (inp == "exit"):
            continue

        elif (inp == "wallet"):
            wallet()

        elif (inp == "help"):
            show_commands()

        #if input is wrong format, continue
        else:
            print("invalid command")



if __name__ == "__main__":
    main()
