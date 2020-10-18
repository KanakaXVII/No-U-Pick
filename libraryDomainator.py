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

#Create the function for adding a new game to the DB
def addNewGame():
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
        main()
    elif doesExist == None:
        print('\nAdding %s' % gameName)
        newGamePost = {"_id": gameId, "gameName": gameName, "genre": genre, "subGenre": subGenre, "rank": 100, "skipCount": 0, "playCount": 0, "vendor": vendor}
        collection.insert_one(newGamePost) 
        main()

#Create function to show list of games
def showGameList():
    fullList = collection.find({})

    for x in fullList:
        print(x['gameName'])
    
    main()

#Create function to randomize a game based on game ranks and common games in the group
def chooseForMe():
    print('Choose for me placeholder')

#Create a function to alter ranks if the game was predetermined
def weChose():
    print('We chose already placeholder')

#Create a function to search for and output the details of a specific game
def searchForGame():
    print('Serach for me placeholder')

#Create the main function that allows selection of the function to be executed
def main():
    #Make a main menu
    operation = input("\nWhat do you want to do?\n\nOptions are:\n1. |Choose for Me|\n2. |Add New Game|\n3. |We Chose Already|\n4. |Show Games|\n5. |Search for Game|\n6. |Exit|\n\n>>> ")
    operation = operation.lower()

    #Determine what function to call
    if operation == 'choose for me' or operation == '1':
        print('\nYou chose "Choose For Me".\n')
        chooseForMe()
    elif operation == 'add new game' or operation == '2':
        print('\nYou chose "Add New Game".\n')
        addNewGame()
    elif operation == 'we chose already' or operation == '3':
        print('\nYou chose "We Chose Already".\n')
        weChose()
    elif operation == 'show games' or operation == '4':
        print('\nYou chose "Show Games".\n')
        showGameList()
    elif operation == 'search for game' or operation == 'search' or operation == '5':
        print('\nYou chose "Search For Game".\n')
        searchForGame()
    elif operation == 'exit' or operation == '6':
        exit()
    else:
        print('Please enter a valid option.')
        main()

#Call the main to start application
main()