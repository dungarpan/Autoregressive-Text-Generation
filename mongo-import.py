import pymongo
import pickle

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["Gutenberg"]
            
collection = db["book-metadata"]

#get book info inside book_dict
book_dict={}
for i in range(1,72):
  print(i)
  pick_name = 'Book-Info/book_dict_' + str(i) + ".pickle"
  with open(pick_name, 'rb') as f:
    temp_book_dict = pickle.load(f)
    book_dict.update(temp_book_dict)

"""
title_dict = {"id":[],
              "Title":[],
              "Author":[],
              "Encoding":[],
              "Language":[],
              "Date Released":[],
              "Pickle": 
              }"""

c=0
for k,v in book_dict.items():

  #Inserting data into title_dict(temp dictionary) from the pickle file which stores book metadata
  title_dict={}
  title_dict["id"] = k
  title_dict["Title"] = v["title"].upper().strip()
  title_dict["Author"] = v["author"].upper().strip()
  if v["encoding"] == "":
    v["encoding"] = "IS0-8859-1"
  title_dict["Encoding"]=v["encoding"].upper().strip()
  if v["language"] == "":
    v["language"] = "English"
  title_dict["Language"]=v["language"].upper().strip()
  book_date = v["release"].split("[")[0].strip()[-4:]
  if book_date.isdigit():
    title_dict["Date Released"]=book_date
  else:
    title_dict["Date Released"]=""
  
  #Insert data entry into Mongodb
  try:
    collection.insert_one(title_dict)
  except:
    print("k: " + str(k))

  c=c+1
  if c<10:
    print(title_dict)
  if c%5000==0:
    print(c)


# db.test1.find({},{"61092":1})
