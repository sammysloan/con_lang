import ipapy

class Word:
    def __init__(self, origin, sylls, syn_func, stress):
        self.origin = origin
        self.sylls = sylls
        self.syn_func = syn_func
        self.stress = stress
    def __repr__(self):
        return repr(self.origin)
    

class Evolution:
    def __init__(self, title, notes):
        self.title = title
        self.notes = notes

    
class Assimilate(Evolution):
    def __init__(self, title, notes, old_list, new_list, 
                pre = False, post = False, skip_stress = False):
        super().__init__(title, notes)
        self.old_list = old_list
        self.new_list = new_list
        self.pre = pre
        self.post = post
        self.skip_stress = skip_stress
    def __repr__(self):
        return repr(self.title)

class Context_Edit(Evolution):
    def __init__(self, title, notes, old_list, new_list, 
                pre = False, post = False, skip_stress = False):
        super().__init__(title, notes)
        self.old_list = old_list
        self.new_list = new_list
        self.pre = pre
        self.post = post
        self.skip_stress = skip_stress
    def __repr__(self):
        return repr(self.title)
    


created_words = []
special_chars = ()

user_words = ("Es.ta.tum ˈär.mä ˈu̯ɪr.ʊm.kʷe ˈkä.noː ˈt̪rɔi̯ː.ae̯ ˈkʷɪ ˈpriː.mʊs̠ ˈäb "
    "ˈoː.rɪs̠ ɪˈ.t̪äl.ʲiäm ˈfäːt̪oː ˈprɔ.fʊ.ɡʊs̠ Läu̯.iːn.iä.kʷe ˈu̯ɛ.nɪt̪ "
    "ˈlʲiːt̪.o.r ˈmʊɫ̪t̪ʊ̃ˑ ˈɪl.lʲɛ ˈɛt̪ ˈt̪ɛr.riːs̠ ˈi̯äk.t̪äː.t̪ʊs ˈɛt̪ "
    "ˈäɫ̪t̪oː u̯iː ˈs̠ʊ.pɛ.rʊm s̠äe̯.u̯äe̯ ˈmɛ.mɔ.rɛ̃ ˈi̯uː.noː.nɪs ˈɔb ˈiːrä̃ˑ")
# ("ath.let.e chom.sky chon.sky tonth hau.zan brid grid me.mo.ry "
# "sko.la sta.tum span ˈka.nɪs ˈmaŋ.nʊs̠ ˈɛs̠t̪ sɛd ˈfeː.leːm ˈpar.wam ˈɛs̠t̪ "
# "ˈka.nɪs ˈfeː.leːm ˈpar.wam ˈmɔr.dɛt")


### PHONEMIC EDITORS ###
def assimilate(target_list, trigger_list, progressive = False, skip_stress = False):
    """
    target_list replaced old_val, trigger_list replaced trigger; this code has 
    not been tested and may need fixing; pay attention to var names. 
    """
    def replace(): 
        return syll.replace(tar_val, target_list[trig_index])

    for word in created_words:
        sylls = word.sylls

        # Begins by checking if an evolving character is in a given syllable.
        for syll_index, syll in enumerate(sylls):
            for tar_val in target_list:
                if tar_val in syll:
                    # Checks if a trigger character is in the next syllable.
                    for trig_index, trig_val in enumerate(trigger_list):
                        # Checks if trigger is progressive/procedes old.
                        if progressive: 
                            if (syll_index - 1 < len(sylls) 
                            and trig_val in sylls[syll_index - 1]):
                                syll = replace()
                        else:
                            if (syll_index + 1 < len(sylls) 
                            and trig_val in sylls[syll_index + 1]):
                                syll = replace()
                                sylls[syll_index] = syll
                                                


""" 
WHAT ARE MY NEEDS FOR CONTEXT EDIT?
    new and old variables must be changed to lists.
        "." syll breaks must be added to pre and fol lists to avoid replacement errors.
         
"""

def contextual_edit(old_list, new_list, pre_list = False, post_list = False, 
                except_pre = [], except_post = [], skip_stress = False):

    def check_except(sylls_str, old, except_pre, except_post, i): 
        for pre in except_pre:

            if pre in sylls_str[i -len(pre):i]: 
                return True
        
        for post in except_post:
            if post in sylls_str[i:i + len(old) + len(post)]:
                return True
        return False

    def match_post(sylls_str, old, post_list, i):
        # Extract substr; starting at sum i and old
        # End at sum of i, old, and post
        post_match = any(sylls_str[i + len(old): i + len(old)
        + len(post)] == post for post in post_list)
        return post_match # Return boolean


    def match_pre(sylls_str, pre_list, i):       
        # Extract substr; starting at i - len(pre)
        # End at i; (the position where "old" starts)
        pre_match = any(sylls_str[max(0, i - len(pre)):i] == pre 
                        for pre in pre_list)
        return pre_match # Retrun boolean

    def replace(sylls_str, old, i):
        # old_index = old_list.index[old]

        sylls_str = (sylls_str[:i] + "¡!¡" + sylls_str[i + len(old):])
        return sylls_str


    if pre_list: # Add syll breaks to each pre value
        temp = [pre + "." for pre in pre_list]
        pre_list = pre_list + temp
    if post_list: # Add syll breaks to each post value
        temp = ["." + post for post in post_list]
        post_list = post_list + temp


    # Begin main loop
    for word in created_words:
        # List stores new vals; later used to replace "!¡!"
        new_vals = []


        if skip_stress: # Temp remove stress so edits are not made
            if len(word.sylls) < 2: # Skip monosyll words
                continue
            stress_syll = stress_remove(word)


        # Convert sylls to a string for easier editing        
        sylls_str = ".".join(word.sylls)


        for old in old_list:
            i = 0 # Tracks later movement through syll_str
            while i < len(sylls_str): # Avoid index errors


                # Extract substr from syll_str; start at i, extend len(old)
                if sylls_str[i:i + len(old)] == old: # if substr == old


                    # Check if any except value adjacent to old
                    if except_post or except_post:                   
                        if check_except(sylls_str, old, except_pre, except_post, i):
                            i += 1 # Moves while loop to next character
                            continue

                    if pre_list and post_list:
                        pre_bool = match_pre(sylls_str, pre_list, i)
                        post_bool = match_post(sylls_str, old, post_list, i)


                        if pre_bool and post_bool:
                            # Create var that holds new val
                            index = old_list.index(old)
                            new_vals.append(new_list[index])
                            sylls_str = replace(sylls_str, old, i)
                
                    elif pre_list:
                        pre_bool = match_pre(sylls_str, post_list, i)

                        if pre_bool: 
                            index = old_list.index(old)
                            new_vals.append(new_list[index])
                            sylls_str = replace(sylls_str, old, i)
                            
                            
                    elif post_list:
                        post_bool = match_post(sylls_str, old, post_list, i)
                        if post_bool: 
                            index = old_list.index(old)
                            new_vals.append(new_list[index])
                            sylls_str = replace(sylls_str, old, i)
                        
                    else:
                            index = old_list.index(old)
                            new_vals.append(new_list[index])
                            sylls_str = replace(sylls_str, old, i)
                i += 1 # Moves while loop to next character

            if new_vals:
                for val in new_vals:
                    sylls_str = sylls_str.replace("¡!¡", val, 1)

            if skip_stress: # Reinsterts stressed syll
                sylls_str = sylls_str.replace("!!!", stress_syll)
            
            word.sylls = sylls_str.split(".")

def stress_remove(word): 
    stress_syll = word.sylls[word.stress] # Stressed syll saved
    word.sylls[word.stress] = "!!!"
    return stress_syll

def stress_edit(new_list, old_list, pre = False, post = False):
    ...

def syllabic_edit(new_list, old_list, pos):
    # Adds stress markers to old vals in order to find all relevant phonemes.
    update = ["ˈ" + old for old in old_list]
    old_list = old_list + update

    for word in created_words:
        sylls_str = ".".join(word.sylls)
        i = 0
        for old in old_list:
            if pos == "first" and sylls_str.startswith(old):
                sylls_str = sylls_str.replace(old, new_list[i])
            elif pos == "last" and sylls_str.endswith(old):
                sylls_str = sylls_str.replace(old, new_list[i])
            else: i = i + 1
        word.sylls = sylls_str.split(".")



"""
Function must be able to edit select sections of a syllable without replacing the whole thing.
Example: Es.ta.tum --> Es.ta.toom - Avoid Es.ta.oom
Consider doing somethinng like [i: ]
"""





### GRAMMATICAL EDITORS
def grammar_edit(syn_func, edit_type):
    # Both parameters will later be selected by drop-down menus in a widget
    for word in created_words:
        if syn_func == word.syn_func:
            # Should I enter all the functions into a class which can be called
            ...


### WORD EDITORS ###
def create_word(word):
    def find_stress (sylls):
        for syllable in sylls:
            if syllable.startswith("ˈ"):
                stress = sylls.index(syllable)
                return stress
            
    origin = word
    # Turns the original input in to a list of syllables
    sylls = word.split(".")
    stress = (find_stress(sylls))

    # Replace this later with popups:
    # syn_func = input("Define syntactic function: ")
    syn_func = "v"

    return [origin, sylls, syn_func, stress]
        
def insert_word():
    word = input("Add word: ")
    pos = int(input("Define position: "))
    origin, sylls, syn_func, stress = create_word(word)
    created_words.insert(pos, Word(origin, sylls, syn_func, stress))

### MAIN FUNCTIONS ###
def initialize_list(user_input):
    user_words = user_input.split(" ")
    for word in user_words:
        origin, sylls, syn_func, stress = create_word(word)

        created_words.append(Word(origin, sylls, syn_func, stress))

def make_output():
    output = []
    for word in created_words:
        output.append(".".join(word.sylls))

    print(" ".join(output))


def main():
    initialize_list(user_words)

    syllabic_edit(["oom"], ["um"], "last")
    contextual_edit(["t"], ["T"], False, False, ["Z"], ["S", "h"])
    contextual_edit(["z", "r"], ["z", ">:)"], ["ä"], ["m"])
    contextual_edit(["k"], ["tʃ"], False, ["a", "ä", "ɑ", "ɒ"])
    contextual_edit(["ɪl", "il", "m.ni", "ni" "ak"], [ "ʎ",  "ʎ", "ɲ", "ɲ", "ç"])
    contextual_edit(["p̪", "p", "t̪", "t", "k"], ["b̪", "b",  "d̪", "d", "g"])
    contextual_edit(["p̪p̪", "pp", "t̪t̪", "tt", "kk"], ["p̪", "p", "t̪", "t", "k"])
    contextual_edit(["aː", "äː", "ä", "eː", "e", "ɛ", "ɪ", "iː", "oː", "ʊ", "uː"], ["a", "a", "a", "e", "iɛ", "iɛ", "e", "i", "o", "o", "u"])
    syllabic_edit(["sp̪", "sp", "st̪", "st", "sk"], ["es.p̪", "es.p", "es.t̪", "es.t", "es.k"], "first")

    make_output()

    """

    Research json - JSON takes complex objects and turns them into a  

    Save each preset as a table in the same database.
    Each row is a preset --> have a column name/ID, column for data that has been JSONified. 
    Query for preset name > pull JSON data from column > convert data back to object.

    DTO - you don't want funcs/method stored in databases. 
    Create a data transfer object - it acts as an interface 


    Create a master function - "evolve" that requires all 

    Make a specific DAO - class that interacts with the data base (which otherwise should not be interacted with).
    Helps with debugging and code cleanliness. 

    LOOK INTO LATER
    UML - Universal Modeling Language - way of drawing out code. 
        Sequence diagram. 

    """


    # for word in created_words:
    #     print(word.sylls)

if __name__ == '__main__':
    main()

# Write a function that maintains voicing using even or odd index. 
