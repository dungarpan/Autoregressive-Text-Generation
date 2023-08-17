import streamlit as st
import requests
from pymongo import MongoClient
import pickle
import random
import string


#Predict the next word in the list
@st.cache
def predict_next_word(this_kgram, freq_dict):
    if this_kgram not in freq_dict:
      return None
    weighted_list = []
    for k in freq_dict[this_kgram]:
        for x in range(freq_dict[this_kgram][k]):
            weighted_list.append(k)
    return random.choice(weighted_list)


#Predict the whole paragraph using predict_next_word
@st.cache
def predict_paragraph(start_kgram, k, freq_dict, gen_length=300):
    gen_para = start_kgram

    for i in range(gen_length):
      kgram = " ".join(gen_para[-k:])
      new_word = predict_next_word(kgram, freq_dict)
      if new_word is None:
        return gen_para
      else:
        gen_para.append(new_word)
    return gen_para


def next_word(freq_dict_test):
    start_test = random.choice(list(freq_dict_test.keys())).split()


#Retrieve the next word frequency dictionary of the given ngram
@st.cache
def retrieve_freq_dict(id):
    i = int(id/100)+1
    fpath = 'Compressed/Gutenberg-Books-WS/book_words_dict_' + str(i) + ".pickle"
    with open(fpath, 'rb') as file:
        # Load the contents of the pickle file
        data = pickle.load(file)
        data = data[id]

        return i, data


# Connect to MongoDB
@st.cache
def get_authors():
    client = MongoClient('mongodb://localhost:27017')
    db = client['Gutenberg']
    collection = db['metadata']
    # Aggregation pipeline
    pipeline = [
        {
            '$group': {
                '_id': '$Author',
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'count': -1}
        },
        {
            '$project': {
                '_id': 1,
            }
        }
    ]

    # Execute the aggregation pipeline
    result = collection.aggregate(pipeline)

    authors_temp = list(result)

    c=0
    authors=[]
    for author in authors_temp:
        if c>3:
            authors.append(author['_id'])
        c=c+1
    

    return authors

#@st.cache
def get_books_of_author(author):
    client = MongoClient('mongodb://localhost:27017')
    db = client['Gutenberg']
    collection = db['metadata']
    result = collection.find({'Author': author},{"Title":1,"_id":0})
    books_temp = list(result)
    books=[]
    for book in books_temp:
        books.append(book['Title'])
    return books

#@st.cache
def get_book_id(title):
    client = MongoClient('mongodb://localhost:27017')
    db = client['Gutenberg']
    collection = db['metadata']
    result = collection.find({'Title': title},{"id":1,"_id":0})
    id_temp = list(result)
    id=[]
    for book in id_temp:
        id.append(book['id'])
    return id


@st.cache
def get_random_ngram(freq_dict_test):
    kgram_start_choices = random.choices(list(freq_dict_test.keys()), k=30)
    for kgram in kgram_start_choices:
        if any(char in string.punctuation for char in kgram):
            kgram_start_choices.remove(kgram)

    return kgram_start_choices

def main():
    st.title("Project Gutenberg Text Gen")
    st.image("library.jfif")
    authors_list = get_authors()
    selected_author = st.selectbox('Select an author', authors_list)
    st.write("Your author is", selected_author)

    book_list = get_books_of_author(selected_author)
    selected_book = st.selectbox('Select a book', book_list)
    st.write("Great choice! You selected: ", selected_book)

    id_list = get_book_id(selected_book)
    id = id_list[0]

    start, freq_dict_test = retrieve_freq_dict(id)
    #selected_start_kgram = random.choice(list(freq_dict_test.keys())).split()
    kgram_start_choices = get_random_ngram(freq_dict_test)

    
    #for i in range(len(kgram_start_choices)):
    #    kgram_start_choices[i] = kgram_start_choices[i].capitalize()

    selected_start_kgram = st.selectbox('Select the starting words of the paragraph', kgram_start_choices)

    start_kgram = selected_start_kgram.split()

    para_length = st.slider('Select paragraph length', min_value=20, max_value=500, step=1)

    with st.form("my_form"):
        submit_button = st.form_submit_button(label='Generate text')

    if submit_button:
        gen_para = predict_paragraph(start_kgram, 3, freq_dict_test, para_length)
        gen_para = " ".join(gen_para)
        st.write(gen_para)

if __name__ == '__main__':
    main()