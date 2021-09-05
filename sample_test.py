a_dictionary = {"a" : 1, "b" : 2}

file = open("sample.txt", "w")
str_dictionary = repr(a_dictionary)
file.write("a_dictionary = " + str_dictionary + "\n")
# "\n" creates newline for next write to file

file.close()