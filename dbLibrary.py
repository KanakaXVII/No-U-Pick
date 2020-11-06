"""
    Author: Jarrin Sacayanan
    Github: https://www.github.com/KanakaXVII/MongoDB-Test

    Purpose: This program is made to interact with a Mongo DB I created. The app's purpose is to create game libraries for multiple people.
        The game libraries will keep track of game play count, game information, and generate a randomized game based on a game's rank in case
        players become indecisive on what to play.

    Notes: Please refer to the README for instructions on how to set login credentials.
"""

import pymongo
from pymongo import MongoClient
import math
import random
import myCreds
import os

#Set some global variables...a secret tool that will help us later 
collection = None
db = None
cluster = None
loginTimeout = 0

def login():
    myCreds.setVar()

    loginUser = os.environ.get('MONGO_USERNAME')
    loginPass = os.environ.get('MONGO_PASSWORD')

    loginURL = r"mongodb+srv://%s:%s@game-library.299lb.mongodb.net/Game-Library?retryWrites=true&w=majority"
    loginCreds = (loginUser, loginPass)

    timeoutIter = 1

    global cluster
    cluster = MongoClient(loginURL % loginCreds, serverSelectionTimeoutMS=timeoutIter)

    global loginTimeout
    if loginTimeout <= 10:
        try:
            cluster.server_info()
        except:
            loginTimeout += 1
            login()
    else:
        print('Timed Out...')
        exit()

    global db 
    db = cluster["Game-Library"]

    print('Logged in as %s' % loginUser)

    setFocus()

#Manually log in as a different user
def manLogin():
    loginUser = input('Username: ')
    loginPass = input('Password: ')

    loginURL = r"mongodb+srv://%s:%s@game-library.299lb.mongodb.net/Game-Library?retryWrites=true&w=majority"
    loginCreds = (loginUser, loginPass)

    timeoutIter = 1

    global cluster
    cluster = MongoClient(loginURL % loginCreds, serverSelectionTimeoutMS=timeoutIter)

    global loginTimeout
    if loginTimeout <= 10:
        try:
            cluster.server_info()
        except:
            loginTimeout += 1
            login()
    else:
        print('Timed Out...')
        exit()

    global db 
    db = cluster["Game-Library"]

    print('Logged in as %s' % loginUser)

    setFocus()

#Create a function that sets the database that will be worked with
def setFocus():
    print('\n\nChanging Database...\n\n')

    gamertag = input("Gamertag:\n>>> ")
    global collection 
    collection = db["Library-%s" % gamertag]

    print("Opening Library for %s" % gamertag)

    main()

#Create the function for adding a new game to the DB
def addNewGame():
    #Create temporary variables to collect the informatio that will go into the DB
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
        newGamePost = {"gameName": gameName, "genre": genre, "subGenre": subGenre, "rank": 100, "skipCount": 0, "playCount": 0, "vendor": vendor}
        collection.insert_one(newGamePost) 
    
    main()

#Create function to show list of games
def showGameList():
    fullList = collection.find({})

    for x in fullList:
        print(x['gameName'])
    
    main()

#Create a function to get a list of players for randomizer
def getPlayers():
    tempListPlayers = []

    #Get list of people playing
    print('Who is playing? Type "Done" when everyone is entered.\n')

    isNotDone = True
    while isNotDone:
        tempInput = input('>>> ')
        if tempInput.lower() == 'done':
            break
        else:
            tempListPlayers.append(tempInput)

    chooseForMe(tempListPlayers)

#Create function to randomize a game based on game ranks and common games in the group
def chooseForMe(tempListPlayers):
    listPlayers = []
    
    #Call function to get player names
    listPlayers = tempListPlayers
    numPlayers = len(listPlayers)
    
    #Pull game lists from multiple users
    colList = []
    for x in listPlayers:
        currentPlayer = x
        playerString = 'Library-%s' % currentPlayer
        colList.append(playerString)
    
    #Weed out uncommon games
    colCount = 0
    finalList = []
    while colCount < numPlayers:
        tempList = []
        tempCollection = db[colList[colCount]]
        tempColList = tempCollection.find({})
        
        if colCount == 0:
            for x in tempColList:
                tempList.append(x['gameName'])
            
            for x in tempList:
                finalList.append(x)

        elif colCount > 0 and colCount < numPlayers:
            for x in tempColList:
                tempList.append(x['gameName'])

            firstSet = set(tempList)
            secondSet = set(finalList)
            commonSet = firstSet.intersection(secondSet)
            finalList = commonSet
        
        else:
            break
        
        colCount += 1

    #Populate list used for random selection
    selectList = []
    for x in finalList:
        selectList.append(x)
    
    #Pick game at random
    randomSelector = random.randint(0,len(finalList) - 1)
    selectedGame = selectList[randomSelector]
    print('\nRandom Game: ',selectedGame)

    #Pull ranks of game for each person
    ranksForGame = []
    
    rankCounter = 0
    while rankCounter < numPlayers:
        tempCollection = db[colList[rankCounter]]
        tempColList = tempCollection.find({'gameName': selectedGame})
        
        for x in tempColList:
            ranksForGame.append(x['rank'])

        rankCounter += 1
    
    #Generate a random to determine if the game passes
    averageRank = 0
    for x in ranksForGame:
        averageRank += x
    
    averageRank = averageRank / len(ranksForGame)
    print('Average Rank: ',averageRank)
    
    #Determine if the game passes with random
    doCont = True
    while doCont:
        doPlay = random.random() * 100
        print('Random Generated: ',doPlay)
        
        if doPlay <= averageRank:
            print('%s Passed' % selectedGame)
            doCont = False
        else:
            doCont = True
    
    playGame = input('Do you want to play ' + selectedGame + '?\n>>> ')
    playGame = playGame.lower()

    #Determine if the game needs to be rerolled or not
    playGameBool = True
    while playGameBool:
        #If they don't want to play, send them to the reroll function
        if playGame == 'no' or playGame == 'n':
            playGameBool = False
            doReroll(colList, numPlayers, selectedGame, tempListPlayers)
        #If they do want to play, edit the rank and play count of the games
        elif playGame == 'yes' or playGame == 'y':
            playGameBool = False
            
            #Edit the rank and play count here
            counter = 0

            print('Changing rank for %s...' % selectedGame)

            try:
                while counter < numPlayers:
                    tempCollection = db[colList[counter]]
                    tempColList = tempCollection.find({'gameName': selectedGame})

                    currentRank = 0
                    currentPlayCount = 0

                    for x in tempColList:
                        currentRank = x['rank']
                        currentPlayCount = x['playCount']

                    newRank = currentRank + 1
                    newPlayCount = currentPlayCount + 1

                    if newRank >= 100:
                        newRank = 100

                    changeFilter = {'gameName': selectedGame}
                    editValues = {'$set': {'rank': newRank, 'playCount': newPlayCount}}
                    tempCollection.update_one(changeFilter, editValues)
                    
                    counter += 1
            
                    print('\nThe rank for %s has been increased! Have fun gaming!\n' % selectedGame)
                    goToMain = input('\nDo you want to do something else?\n>>> ')
                    goToMain = goToMain.lower()
            
            except:
                print('Could not write to DB...')
                main()

            #Determine if user wants to go to the main menu or not
            goToMainBool = True
            while goToMainBool:
                if goToMain == 'yes' or goToMain == 'y':
                    goToMainBool = False
                    main()
                elif goToMain == 'no' or goToMain == 'n':
                    goToMainBool = False
                    exit()
                else:
                    print('Please enter a valid response')
                    playGameBool = True
        
        else:
            print('Please enter a valid response.')
            playGameBool = True

#You can pass the thing just this once. It'll be our secret ;)
#Create a function to perform the reroll function
def doReroll(colList, numOfPlayers, selectedGame, tempListPlayers):
    counter = 0
    
    print('\nRerolling...')
    
    try:
        while counter < numOfPlayers:
            tempCollection = db[colList[counter]]
            tempColList = tempCollection.find({'gameName': selectedGame})

            currentRank = 0
            currentSkipCount = 0

            for x in tempColList:
                currentRank = x['rank']
                currentSkipCount = x['skipCount']
            
            newRank = currentRank - 2
            newSkipCount = currentSkipCount + 1

            if newRank >= 0:
                changeFilter = {'gameName': selectedGame}
                editValues = {'$set': {'rank': newRank, 'skipCount': newSkipCount}}
                tempCollection.update_one(changeFilter, editValues)

            counter += 1
    except:
        print('Could not write to DB...')
        main()
    
    print('Rank for %s has been reduced.' % selectedGame)
    chooseForMe(tempListPlayers)

#Create a function to alter ranks if the game was predetermined
def weChose():
    chosenGame = input('What game did you play?\n>>> ')
    
    doAlterRecord = collection.find({'gameName': chosenGame})

    currentRank = 0
    for x in doAlterRecord:
        currentRank = x['rank']
    
    newRank = currentRank + 1

    if newRank < 100:
        changeFilter = {'gameName': chosenGame}
        editValues = {"$set": {'rank': newRank}}
        collection.update_one(changeFilter, editValues)
    
    main()

#Create a function to search for and output the details of a specific game
def searchForGame():
    searchCriteria = input('What do you want to search by?\nOptions are:\n1. |Game Name|\n2. |Genre|\n3. |Rank|\n4. |Play Count|\n5. |Skip Count|\n\n6. |Back|\n\n>>> ') #Yay for menus
    searchCriteria = searchCriteria.lower()

    #Create conditions to search by
    if searchCriteria == 'game' or searchCriteria == 'name' or searchCriteria == '1':
        searchString = input('\nGame:\n>>> ')
        searchResult = collection.find({"gameName": searchString})
        
        #Check to see if game exists
        #Placeholder


        contBool = True
        while contBool:
            #Print the results here instead of the default for more detail
            for x in searchResult:
                print('\nGame: ',x['gameName'],'\nVendor: ',x['vendor'],'\nRank: ',x['rank'],'\nSkip Count: ',x['skipCount'],'\nPlay Count: ',x['playCount'],'\n\n')

            doMoreBool = True
            while doMoreBool:
                doMore = input('Do you want to do something to this game?\n\n1. Edit\n2. Delete\n3. Back\n4. Main Menu\n\n>>> ')
                doMore = doMore.lower()

                if doMore == '1' or doMore == 'edit':
                    doEditGame(collection, searchString)
                    doMoreBool = False

                elif doMore == '2' or doMore == 'delete':
                    valid1 = input('Are you sure you want to delete %s?\n>>> ' % searchString)
                    valid1 = valid1.lower()

                    delBool = True
                    while delBool:
                        if valid1 == 'yes' or valid1 == 'y':
                            print('Deleting %s...\n' % searchString)
                            collection.delete_one({'gameName': searchString})
                            delBool = False
                            main()
                        elif valid1 == 'no' or valid1 == 'n':
                            print('Cancelling...\n')
                            
                            for x in searchResult:
                                print('\nGame: ',x['gameName'],'\nVendor: ',x['vendor'],'\nRank: ',x['rank'],'\nSkip Count: ',x['skipCount'],'\nPlay Count: ',x['playCount'],'\n\n')
                            
                            delBool = False
                        doMoreBool = False

                elif doMore == '3' or doMore == 'back':
                    searchForGame()
                    doMoreBool = False

                elif doMore == '4' or doMore == 'main menu' or doMore == 'main' or doMore == 'menu':
                    main()
                    doMoreBool = False

                else:
                    print('Please enter a valid response...')
                    doMoreBool = True

    elif searchCriteria == 'genre' or searchCriteria == '2':
        searchString = input('\nGenre:\n>>> ')
        searchResult = collection.find({"$or":[{"genre": searchString}, {"subGenre": searchString}]})
    elif searchCriteria == 'rank' or searchCriteria == '3':
        searchString = input('\nRank:\n>>> ')
        searchString = int(searchString)
        searchResult = collection.find({"rank": searchString})
    elif searchCriteria == 'play count' or searchCriteria == '4':
        searchString = input('\nPlay Count:\n>>> ')
        searchString = int(searchString)
        searchResult = collection.find({"playCount": searchString})
    elif searchCriteria == 'skip count' or searchCriteria == '5':
        searchString = input('\nSkip Count:\n>>> ')
        searchString = int(searchString)
        searchResult = collection.find({"skipCount": searchString})
    elif searchCriteria == 'back' or searchCriteria == '6':
        main()
    else:
        print('Please enter a valid option.')
        searchForGame()
    
    #Iterate through results and print them
    for x in searchResult:
        print(x['gameName'])
    
    main()

#Create a function to edit within the search
def doEditGame(collection, gameName):
    editGameName = input('\nGame Name:\n>>> ')
    editGenre = input('Genre:\n>>> ')
    editSubGenre = input('Sub Genre:\n>>> ')
    editVendor = input('Vendor\n>>> ')

    changeFilter = {'gameName': gameName}
    editValues = {"$set": {"gameName": editGameName, "genre": editGenre, "subGenre": editSubGenre, "vendor": editVendor}}
    collection.update_one(changeFilter, editValues)
        
    main()

def pickFrom5():
    print('You found me...\nEnter 5 Games...')
    yeOleGames = [0] * 5
    
    x = 0
    while x < 5:
        yeOleGames[x] = input('>>> ')
        x += 1

    yeOleRando = random.randint(0,4)
    print('Random: %s' % yeOleRando)

    print('\nYou will play %s.' % yeOleGames[yeOleRando])

    main()

#Note to self...DO NOT PASS THE THINGY PLEASE AND THANKS
#Create the main function that allows selection of the function to be executed
def main():
    #Make a main menu
    operation = input("\nWhat do you want to do?\n\nOptions are:\n1. Choose for Me\n2. Add New Game\n3. We Chose Already\n4. Show Games\n5. Search for Game\n6. Change Library\n7. Pick From 5\n\n8. Exit\n\n>>> ")
    operation = operation.lower()

    #Determine what function to call
    if operation == 'choose for me' or operation == '1':
        print('\nYou chose "Choose For Me".\n')
        getPlayers()
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
    elif operation == 'change library' or operation == '6':
        setFocus()
    elif operation == 'pick from 5' or operation == '7':
        pickFrom5()
    elif operation == 'exit' or operation == '8':
        exit()
    elif operation == 'change user':
        #Close cluster
        global cluster
        cluster.close()

        #Reset global variables
        cluster = None
        db = None
        collection = None

        global loginTimeout
        loginTimeout = 0

        manLogin()
    else:
        print('Please enter a valid option.')
        main()

#Call the login function to start after setting the initial DB login and focus
login()

"""
    I see you looking at this code...It's okay...It can be our little secret ;)
    I just ask that you don't steal anything and pass it off as your own...I worked very hard to teach myself this stuff.
    If you have any suggestions or bugs, please let me know so I can try to make this program better!
    
    Thank you bby :*
    ~Jay S
"""

# To Do:
# - Show genre list in search
# - Instead of "show games", you can do a selection to show an input
# - Quick Add Feature...Add all game information from someone elses library into your own
# - Add new attribute to DB Objects (isMulti)
# - Make validation for player limit...attribute (maxPlayers)
# - Add something to validate users for the chooseForMe selection
# - Add something to stop crash on add game for other libraries
# - Add try/except to addNewGame to prevent crash
# - Remove doCont
# - Add removeGame() function
# - Move the player name input outside of the chooseForMe function
# - Make it impossible to not enter any players to prevent a crash