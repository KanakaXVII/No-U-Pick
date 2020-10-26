"""
    Author: Jarrin Sacayanan
    Github: https://www.github.com/KanakaXVII/MongoDB-Test

    Purpose: This program is made to interact with a Mongo DB I created. The app's purpose is to create game libraries for multiple people.
        The game libraries will keep track of game play count, game information, and generate a randomized game based on a game's rank in case
        players become indecisive on what to play.
    
"""

import pymongo
from pymongo import MongoClient
import pprint
import math
import random

#Set some global variables...a secret tool that will help us later 
collection = None
db = None
cluster = None

def login():
    login = input('DB Username: ')
    password = input('DB Password: ')

    loginURL = r"mongodb+srv://%s:%s@game-library.299lb.mongodb.net/Game-Library?retryWrites=true&w=majority"
    loginCreds = (login, password)

    timeoutIter = 1

    global cluster
    cluster = MongoClient(loginURL % loginCreds, serverSelectionTimeoutMS=timeoutIter)
    cluster.server_info()

    global db 
    db = cluster["Game-Library"]

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
    doCont()

#Create function to show list of games
def showGameList():
    fullList = collection.find({})

    for x in fullList:
        print(x['gameName'])
    
    #Ask if user wants to continue
    doCont()

#Create a function to get a list of players for randomizer
def getPlayers():
    print('placeholder')

#Create function to randomize a game based on game ranks and common games in the group
def chooseForMe():
    listPlayers = []
    
    #Get list of people playing
    print('Who is playing? Type "Done" when everyone is entered.\n')
    
    isNotDone = True
    while isNotDone:
        tempInput = input('>>> ')
        if tempInput.lower() == 'done':
            break
        else:
            listPlayers.append(tempInput)
    numOfPlayers = len(listPlayers)
    
    #Pull game lists from multiple users
    colList = []
    for x in listPlayers:
        currentPlayer = x
        playerString = 'Library-%s' % currentPlayer
        colList.append(playerString)
    
    #Weed out uncommon games
    colCount = 0
    finalList = []
    while colCount < numOfPlayers:
        tempList = []
        tempCollection = db[colList[colCount]]
        tempColList = tempCollection.find({})
        
        if colCount == 0:
            for x in tempColList:
                tempList.append(x['gameName'])
            
            for x in tempList:
                finalList.append(x)

        elif colCount > 0 and colCount < numOfPlayers:
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
    print('Random Game: ',selectedGame)

    #Pull ranks of game for each person
    ranksForGame = []
    
    rankCounter = 0
    while rankCounter < numOfPlayers:
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

    doPlay = random.random() * 100
    print('Random Generated: ',doPlay)
    
    #Determine if the game passes with random
    doCont = True
    while doCont:
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
            doReroll(colList, numOfPlayers, selectedGame)
        #If they do want to play, edit the rank and play count of the games
        elif playGame == 'yes' or playGame == 'y':
            playGameBool = False
            
            #Edit the rank and play count here
            counter = 0

            print('Changing rank for %s...' % selectedGame)

            while counter < numOfPlayers:
                tempCollection = db[colList[counter]]
                tempColList = tempCollection.find({'gameName': selectedGame})

                currentRank = 0
                currentPlayCount = 0

                for x in tempColList:
                    currentRank = x['rank']
                    currentPlayCount = x['playCount']

                newRank = currentRank + 1
                newPlayCount = currentPlayCount + 1

                if newRank < 100:
                    changeFilter = {'gameName': selectedGame}
                    editValues = {'$set': {'rank': newRank, 'playCount': newPlayCount}}
                    tempCollection.update_one(changeFilter, editValues)
                
                counter += 1
            
            print('\nThe rank for %s has been increased! Have fun gaming!\n' % selectedGame)
            goToMain = input('\nDo you want to do something else?\n>>> ')
            goToMain = goToMain.lower()

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

#Create a function to perform the reroll function
def doReroll(colList, numOfPlayers, selectedGame):
    counter = 0
    
    print('Rerolling...')
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
    
    print('Rank for %s has been reduced.' % selectedGame)
    chooseForMe()

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
    searchCriteria = input('What do you want to search by?\nOptions are:\n1. |Game Name|\n2. |Genre|\n3. |Rank|\n4. |Play Count|\n5. |Skip Count|\n\n6. |Back|\n\n>>> ')
    searchCriteria = searchCriteria.lower()

    #Create conditions to search by
    if searchCriteria == 'game' or searchCriteria == 'name' or searchCriteria == '1':
        searchString = input('\nGame:\n>>> ')
        searchResult = collection.find({"gameName": searchString})
        
        #Print the results here instead of the default for more detail
        for x in searchResult:
            print('\nGame: ',x['gameName'],'\nVendor: ',x['vendor'],'\nRank: ',x['rank'],'\nSkip Count: ',x['skipCount'],'\nPlay Count: ',x['playCount'],'\n\n')

        doEditBool = True
        while doEditBool:
            doEdit = input('Do you want to edit the game?\n>>> ')
            doEdit = doEdit.lower()

            if doEdit == 'yes' or doEdit == 'y':
                doEditGame(collection, x['gameName'])
                doEditBool = False
            elif doEdit == 'no' or doEdit == 'n':
                main(collection)
                doEditBool = False
            #placeholder
            else:
                print('Please enter a valid response...')
                doEditBool = True

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

#Create a function to ask if the user wants to do something else
def doCont():
    doContStr = input('\nDo you want to continue? (Yes/No)\n>>> ')

    doContBool = True
    while doContBool:
        if doContStr.lower() == 'yes' or doContStr.lower() == 'y':
            main()
        elif doContStr.lower() == 'no' or doContStr.lower() == 'n':
            print('Happy gaming!')
            db.logout()
            exit()
        else:
            print('Please enter a valid response.')
            doCont()

#Create the main function that allows selection of the function to be executed
def main():
    #Make a main menu
    operation = input("\nWhat do you want to do?\n\nOptions are:\n1. |Choose for Me|\n2. |Add New Game|\n3. |We Chose Already|\n4. |Show Games|\n5. |Search for Game|\n6. |Change Library|\n7. |Change User|\n8. |Exit|\n\n>>> ")
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
    elif operation == 'change library' or operation == '6':
        setFocus()
    elif operation == 'change user' or operation == '7':
        #Close cluster
        cluster.close()

        #Reset global variables
        cluser = None
        db = None
        collection = None

        login()
    elif operation == 'exit' or operation == '8':
        exit()
    else:
        print('Please enter a valid option.')
        main()

#Call the main to start after setting the initial DB login and focus
login()

"""
    I see you looking at this code...It's okay...It can be our little secret ;)
    I just ask that you don't steal anything and pass it off as your own...I worked very hard to teach myself this stuff.
    
    Thank you bby :*
    ~Jay S
"""

# Ideas:
# - Show genre list in search
# - Instead of "show games", you can do a selection to show an input
# - Quick Add Feature...Add all game information from someone elses library into your own
# - Add new attribute to DB Objects (isMulti)
# - Make validation for player limit...attribute (maxPlayers)