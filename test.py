def doReroll(collection, colList, numOfPlayers):
    counter = 0
    
    print('Rerolling...')
    while counter < numOfPlayers:
        tempCollection = db[colList[counter]]
        tempColList = tempCollection.find({'gameName': selectedGame})

        currentRank = 0
        for x in tempColList:
            currentRank = x['rank']
        
        newRank = currentRank - 2

        if newRank >= 0:
            changeFilter = {'gameName': selectedGame}
            editValues = {'$set': {'rank': newRank}}
            tempCollection.update_one(changeFilter, editValues)

        counter += 1

# Old reroll code

# def doReroll(collection, colList, numOfPlayers, selectedGame):
#         counter = 0
#         invalidResponse = True
#         while invalidResponse:
#             if playGame == 'no' or playGame == 'n':
#                 print('Rerolling...')
#                 while counter < numOfPlayers:
#                     tempCollection = db[colList[counter]]
#                     tempColList = tempCollection.find({'gameName': selectedGame})

#                     currentRank = 0
#                     for x in tempColList:
#                         currentRank = x['rank']
                    
#                     newRank = currentRank - 2

#                     if newRank >= 0:
#                         changeFilter = {'gameName': selectedGame}
#                         editValues = {'$set': {'rank': newRank}}
#                         tempCollection.update_one(changeFilter, editValues)
                    
#                     elif newRank < 0:
#                         newRank = 0
#                         changeFilter = {'gameName': selectedGame}
#                         editValues = {'$set': {'rank': newRank}}
#                         tempCollection.update_one(changeFilter, editValues)

#                     counter = counter + 1
                
#                 invalidResponse = False

#             elif playGame == 'yes' or playGame == 'y':
#                 main(collection)
#             else:
#                 invalidResponse = True
#         main(collection)