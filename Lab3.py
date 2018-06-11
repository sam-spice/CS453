import Lab1
import string
import glob

def get_smap():
    orig_dict = {('b','f','p','v'): 1,
                 ('c','g','j','k','q','s','x','z'): 2,
                 ('d','t'): 3,
                 ('l'):4,
                 ('m','n'): 5,
                 ('r'):6}
    to_return = {}
    for k, v in orig_dict.items():
        for key in k:
            to_return[key] = v
    return to_return


def get_soundex(to_soundex):
    sMap = get_smap()
    soundex = ''
    if len(to_soundex) < 1:
        return soundex
    soundex += to_soundex[0].upper()
    for char in to_soundex[1:]:
        charCode = sMap.get(char, '-')
        if charCode != soundex[len(soundex) - 1]:
            soundex += str(charCode)
    soundex = soundex.replace('-','')
    if len(soundex) >= 4:
        soundex = soundex[:4]
    else:
        while len(soundex) < 4:
            soundex += '0'

    #print(soundex)
    return soundex


def get_dict():
    stopfile = open('dictionary.txt')
    dict_words = stopfile.read()
    dict_words = dict_words.replace('\n', ' ')
    dict_words = dict_words.replace('\t', ' ')
    dict_words = dict_words.split(' ')
    dict_set = set()

    for word in dict_words:
        new_word = strip_punc(word)
        dict_set.add(new_word.lower())
    dict_set.remove('')
    return dict_set

def get_candidates(to_correct, dictionary):
    to_match = get_soundex(strip_punc(to_correct))
    print('Soundex Code: ' + to_match)
    match_list = list()
    for word in dictionary:
        new_soundex = get_soundex(word)
        if new_soundex == to_match:
            match_list.append(word.lower())
    return match_list

def get_levenshtein_distance(string1, string2):

    value_array = [[0 for x in range(len(string1) + 1)] for y in range(len(string2) + 1)]
    for i in range(len(string1)):
        value_array[0][i + 1] = i + 1
    for i in range(len(string2)):
        value_array[i + 1 ][0] = i + 1

    for j in range(1, len(string2) + 1):
        for i in range(1, len(string1) + 1):
            if string1[i -1] == string2[j - 1]:
                cost = 0
            else:
                cost = 1
            value_array[j][i] = min(value_array[j - 1][i] + 1,
                                    value_array[j][i - 1] + 1,
                                    value_array[j - 1][i - 1] + cost)

    #print('here')
    return value_array[len(value_array) - 1][len(value_array[0]) - 1]

def find_in_range(query_word, candidates):
    in_range = list()
    for word in candidates:
        if get_levenshtein_distance(query_word, word) <= 2:
            in_range.append(word)
    return in_range


def get_sessions():
    finished_dict = dict()
    infile = open('query_log.txt')
    content = infile.read()
    lines = content.split('\n')
    for line in lines[1:]:
        line_split = line.split('\t')
        finished_dict[line_split[0]] = finished_dict.get(line_split[0], list())
        finished_dict[line_split[0]].append(line_split[1].lower())
    #print('here')
    return finished_dict


def get_prior(suggested, stop_set):
    file_list = glob.glob('To_be_posted/*.txt')
    occur = 0
    total = 0
    for file in file_list:
        tokenized = Lab1.tokenize_file(file, stop_set)
        total += len(tokenized)
        occur += tokenized.count(suggested)
    return occur / total



def get_likelihood(original, suggested, query_logs, dict_set):
    denom = 0
    numer = 0
    for value in query_logs.values():
        orig = False
        misspelled = False
        sugg_in_query = False
        for query in value:
            for word in query.split(' '):
                if word not in dict_set:
                    misspelled = True
            if original in query:
                orig = True
                misspelled = True
            if suggested in query:
                sugg_in_query = True
        if sugg_in_query and misspelled:
            denom += 1
        if sugg_in_query  and orig:
            numer += 1
    if denom == 0:
        return 0
    return numer / denom


def correct_word(word_to_correct, stop_set, dict_set, sessions):
    print('Word to Correct: ' + word_to_correct)
    candidates = get_candidates(word_to_correct, dict_set)
    in_range = find_in_range(word_to_correct, candidates)
    suggestions = ''
    tuples = list()
    for word in in_range:
        suggestions += word + ', '
        likelihood = get_likelihood(word_to_correct, word, sessions, dict_set)
        prior = get_prior(word, stop_set)
        tuples.append((word, likelihood * prior))
    print(suggestions[:-2])
    max_tup = max(tuples, key=lambda item: item[1])
    return max_tup[0]

def strip_punc(to_strip):
    table = str.maketrans({key: None for key in string.punctuation})
    new_s = to_strip.translate(table)
    return new_s


def main():
    stop_set = Lab1.get_stopwords()
    dict_set = get_dict()
    sessions = get_sessions()
    while(1):
        query = input('Gimme yo Query: ')
        query = query.lower()
        tokenized_query = query.split(' ')
        for i  in range(len(tokenized_query)):
            if tokenized_query[i] not in dict_set:
                tokenized_query[i] = correct_word(tokenized_query[i], stop_set, dict_set, sessions)
        # rejoin query
        new_query = ''
        for word in tokenized_query:
            new_query += word + ' '
        print("New Query: " + new_query)
        new_query = new_query[:-1]
        best_5, doc_indices = Lab1.query_run(new_query)
        for entry in best_5:
            print(entry.file)


main()
#returned = get_levenshtein_distance('kitten', 'sitting')
#print('there')
logs = get_sessions()
likelihood = get_likelihood('axtor','actor', logs)
prior = get_prior('actor', Lab1.get_stopwords())
print(likelihood)