# Utils for latin lemmatizer

# Drop macrons from string
def drop_macrons(word):
    word = word.replace("ā", "a").replace("Ā", "A")
    word = word.replace("ē", "e").replace("Ē", "E")
    word = word.replace("ī", "i").replace("Ī", "I")
    word = word.replace("ō", "o").replace("Ō", "O")
    word = word.replace("ū", "u").replace("Ū", "U")
    word = word.replace("ȳ", "y").replace("Ȳ", "Y")
    return word
