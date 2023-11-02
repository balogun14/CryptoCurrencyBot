

def convert_first_letter_of_each_word_to_capital(word):
    """
    This converts the first letter ofeach word to a capital letter
    """
    wordArray = word.split(" ")
    joined_word_array = []
    for i in range(0, len(wordArray)):
        individual_word = wordArray[i]
        joined_word = individual_word[0].capitalize() + (individual_word[1:])
        # individual_word[0] = individual_word[0].capitalize()
        joined_word_array.append(joined_word)
    words_joined = " ".join(joined_word_array)
    return words_joined
