def cfl(word):
    """
    This converts the first letter ofeach word to a capital letter
    """
    wordArray = word.split(" ")
    joined_word_array = []
    i = 0
    while i < len(wordArray) and len(wordArray) != 0:
        individual_word = wordArray[i]
        joined_word = individual_word[0].capitalize() + individual_word[1:]
        # individual_word[0] = individual_word[0].capitalize()
        joined_word_array.append(joined_word)
        i += 1
    words_joined = " ".join(joined_word_array)
    return words_joined

