"""
    Author: Jarrin Sacayanan
    Github: https://www.github.com/KanakaXVII/MongoDB-Test

    Purpose: This program is made to interact with a Mongo DB I created. The app's purpose is to create game libraries for multiple people.
        The game libraries will keep track of game play count, game information, and generate a randomized game based on a game's rank in case
        players become indecisive on what to play.
    
    Contributors:
        Theliara - Logical Planning
        Michael D - Use Case Testing
"""

import pymongo
from pymongo import MongoClient

login = input('DB Username: ')
password = input('DB Password: ')

loginURL = "mongodb+srv://%s:%s@game-library.299lb.mongodb.net/<dbname>?retryWrites=true&w=majority"
loginCreds = (login, password)

cluster = MongoClient(loginURL % loginCreds)
db = cluster["Game-Library"]

gamertag = input("Gamertag:\n>>> ")
collection = db["Library-%s" % gamertag]

print("Opening Library for %s" % gamertag)

#Create a function to login
def login():
    
    login = input('DB Username: ')
    password = input('DB Password: ')

    loginURL = "mongodb+srv://%s:%s@game-library.299lb.mongodb.net/<dbname>?retryWrites=true&w=majority"
    loginCreds = (login, password)

    cluster = MongoClient(loginURL % loginCreds)
    db = cluster["Game-Library"]

    setFocus()

#Create a function that sets the database that will be worked with
def setFocus():
    print('\n\nChanging Database...\n\n')

    gamertag = input("Gamertag:\n>>> ")
    collection = db["Library-%s" % gamertag]

    print("Opening Library for %s" % gamertag)

    main(collection)

#Create the function for adding a new game to the DB
def addNewGame(collection):
    #Create temporary variables to collect the informatio that will go into the DB
    gameId = collection.count_documents({})
    gameName = input("Game Name:\n>>> ")
    genre = input("\nGenre:\n>>> ")
    subGenre = input("\nSub Genre:\n>>> ")
    vendor = input("\nVendor:\n>>> ")

    #Validate that the game does not exist already
    doesExist = collection.find_one({"gameName": gameName})

    if doesExist != None:
        print('\nGame already exists')
    
    elif doesExist == None:
        print('\nAdding %s' % gameName)
        newGamePost = {"_id": gameId, "gameName": gameName, "genre": genre, "subGenre": subGenre, "rank": 100, "skipCount": 0, "playCount": 0, "vendor": vendor}
        collection.insert_one(newGamePost) 
    
    #Ask if user wants to continue
    doCont(collection)

#Create function to show list of games
def showGameList(collection):
    fullList = collection.find({})

    for x in fullList:
        print(x['gameName'])
    
    #Ask if user wants to continue
    doCont(collection)

#Create function to randomize a game based on game ranks and common games in the group
def chooseForMe():
    listPlayers = []
    
    print('Who is playing? Type "Done" when everyone is entered.\n')
    while True:
        tempInput = ''
        tempInput = input('>>> ')
        if tempInput.lower != 'done':
            listPlayers.append(tempInput)
            print(listPlayers)
        elif tempInput.lower() == 'done':
            False
            break
    
    for x in listPlayers:
        print(x)

#Create a function to alter ranks if the game was predetermined
def weChose():
    print('We chose already placeholder')

#Create a function to search for and output the details of a specific game
def searchForGame():
    print('Serach for me placeholder')

#Create a function to ask if the user wants to do something else
def doCont(collection):
    doCont = input('\nDo you want to continue? (Yes/No)\n>>> ')

    if doCont.lower() == 'yes' or doCont.lower() == 'y':
        main(collection)
    elif doCont.lower() == 'no' or doCont.lower() == 'n':
        print('Happy gaming!')
        exit()

#Create the main function that allows selection of the function to be executed
def main(collection):
    #Make a main menu
    operation = input("\nWhat do you want to do?\n\nOptions are:\n1. |Choose for Me|\n2. |Add New Game|\n3. |We Chose Already|\n4. |Show Games|\n5. |Search for Game|\n6. |Change Library|\n7. |Change User|\n8. |Exit|\n\n>>> ")
    operation = operation.lower()

    #Determine what function to call
    if operation == 'choose for me' or operation == '1':
        print('\nYou chose "Choose For Me".\n')
        chooseForMe()
    elif operation == 'add new game' or operation == '2':
        print('\nYou chose "Add New Game".\n')
        addNewGame(collection)
    elif operation == 'we chose already' or operation == '3':
        print('\nYou chose "We Chose Already".\n')
        weChose()
    elif operation == 'show games' or operation == '4':
        print('\nYou chose "Show Games".\n')
        showGameList(collection)
    elif operation == 'search for game' or operation == 'search' or operation == '5':
        print('\nYou chose "Search For Game".\n')
        searchForGame()
    elif operation == 'change library' or operation == '6':
        setFocus()
    elif operation == 'change user' or operation == '7':
        login()
    elif operation == 'exit' or operation == '8':
        exit()
    elif operation == 'logout':
        db.logout()
        login()
    else:
        print('Please enter a valid option.')
        main(collection)

#Call the main to start after setting the initial DB login and focus
main(collection)

"""
    I see you looking at this code...It's okay...It can be our little secret ;)
    I just ask that you don't steal anything and pass it off as your own...I worked very hard to teach myself this stuff.
    
    Thank you bby :*
    ~Jay S
"""