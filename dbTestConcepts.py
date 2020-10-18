import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://KanakaXVII:M4sterCh1efK3ef$%@game-library.299lb.mongodb.net/<dbname>?retryWrites=true&w=majority")

db = cluster["Game-Library"]
collection = db["Library-KanakaXVII"]

#Define variables for creating the post
print("New Game Information\n")
gameId = collection.count_documents({})
gameName = input("Game Name:\n>>> ")
genre = input("Genre:\n>>> ")
subGenre = input("Sub Genre:\n>>> ")
rank = 100
skipCount = 0
playCount = 0
vendor = input("Vendor:\n>>> ")

newGamePost = {"_id": gameId, "gameName": gameName, "genre": genre, "subGenre": subGenre, "rank": rank, "skipCount": skipCount, "playCount": playCount, "vendor": vendor}

collection.insert_one(newGamePost)