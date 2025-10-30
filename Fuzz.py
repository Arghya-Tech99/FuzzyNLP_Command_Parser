from rapidfuzz import fuzz, process
# rapidfuzz - built using C++; faster and more efficient

s1 = "demo string one, for fuzzy string matching"
s2 = "for fuzzy string matching, demo string one"

print(fuzz.ratio(s1,s2))
print(fuzz.partial_ratio(s1,s2))
print(fuzz.token_sort_ratio(s1,s2))
print(fuzz.token_set_ratio(s1,s2))

'''
fuzz.ratio(s1,s2) functionality:-
    1. Calculates Levenshtein distance between s1 and s2
    2. Converts that distance into a similarity ratio, expressed as a percentage
'''

'''
The fuzz.partial_ratio() function in the RapidFuzz library 
    1. Used to calculate the similarity score between two strings,
    focusing on whether a substring from one string matches optimally with the other string
'''

'''
fuzz.token_sort_ratio(s1,s2) functionality:-
    1. Splits both input strings into tokens (words).
    2. Sorts these tokens alphabetically.
    3. Joins them back into strings.
    4. Calculates the similarity ratio (like Levenshtein-based ratio) on the sorted strings.
'''

'''
fuzz.token_set_ratio(s1,s2) functionality:-
    1. Extracts the set of unique tokens from both strings.
    2. Finds the intersection (common tokens) and differences.
    3. Computes the ratio based on the combined unique tokens after removing common tokens, 
    effectively measuring how well the strings share the same set of words regardless of order or repetitions.
'''

things = ["Programming","Programming Language","native languages","Coding and programming","react"]
print(process.extract("Programming",things))
print(process.extract("Programming",things, limit = 2))
print(process.extract("Programming",things, scorer=fuzz.ratio, limit = 2))
print(process.extract("rogramming",things, scorer=fuzz.token_sort_ratio, limit = 3))

'''
The process.extract() function in RapidFuzz :-
    1. Match a query string against a list or collection of choices 
    2. Return the best matching strings with their similarity scores.
    
process.extract(query, choices, scorer=fuzz.ratio, limit=5, processor=None, score_cutoff=0)
    1. query: The string to match.
    2. choices: A list (or iterable) of strings to search from.
    3. scorer: The scoring function used to determine similarity (default: fuzz.ratio)
    4. limit: Maximum number of results to return (default is 5).
    5. score_cutoff: Minimum score for an item to be included in the results.
'''