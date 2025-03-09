import ipapy

class Word:
    def __init__(self, origin, sylls, stress):
        self.origin = origin
        self.sylls = sylls
        # syll_stress = integer that points to list entry containing stress
        self.stress = stress
    def __repr__(self):
        return repr(origin)

class Adverb(Word):
    def __init__(self, origin, sylls, stress):
        super().__init__(origin, sylls, stress)

class Noun(Word):
    def __init__(self, origin, sylls, stress, case, num, gender):
        super().__init__(origin, sylls, stress)
        self.case = case
        self.num = num
        self.gender = gender

class Verb(Word):
    def __init__(self, origin, sylls, stress, mood, tense, voice):
        super().__init__(origin, sylls, stress)
        self.mood = mood
        self.tense = tense
        self.voice = voice

created_words = []
original_text = ("han.bag in.plo.sion")
                 # "ˈka.nɪs ˈmaŋ.nʊs̠ ˈɛs̠t̪ sɛd ˈfeː.leːm ˈpar.wam ˈɛs̠t̪"
                 #ˈka.nɪs ˈfeː.leːm ˈpar.wam ˈmɔr.dɛt")

cons_by_manner = {
    "nasal" : ("m̥", "m", "ɱ̊", "ɱ", "!", "n̼", "!", "!", "n̥", "n", "!",
        "!", "ɳ̊", "ɳ", "ɲ̊", "ɲ", "ŋ̊", "ŋ", "ɴ̥", "ɴ", "!", "!", "!",
        "!"),
   "plosive" : ("p", "b", "p̪", "b̪", "t̼", "d̼", "!", "!", "t", "d", "!",
        "!", "ʈ", "ɖ", "c", "ɟ", "k," "ɡ", "q", "ɢ", "ʡ", "!", "ʔ",
        "!"),}


def assimilate(old, trigger, skip_stress = False):
    for word in created_words:
        sylls = word.sylls

        for syll_index, syll in enumerate(sylls):
            for old_val in old:
                if old_val in syll:
                    for trig_index, trig_val in enumerate(trigger):
                        if trig_val in sylls[syll_index + 1]:
                            syll = syll.replace(old_val, old[trig_index])
                            print(sylls)

def create_words():
    user_words = original_text.split()
    for word in user_words:
        origin = word
        # Turns the original input in to a list of syllables
        sylls = word.split(".")
        stress = (stress_find(sylls))

        p_o_s = "verb"
        # p_o_s = input(f"Define part of speech for {word}: ")

        if p_o_s == "adverb":
            created_words.append(Adverb(origin, sylls, stress))
            obj = Adverb()

        if p_o_s in ("adj", "noun"):
            case = "x"
            num = "x"
            gender = "x"

            created_words.append(Noun(origin, sylls, stress, case, num, gender))
        
        elif p_o_s == "verb":
            mood = "x"
            tense = "x"
            voice = "x"

            created_words.append(Verb(origin, sylls, stress, mood, tense, voice))

def contextual_edit(new, old, pre = False, fol = False, skip_stress = False):
    def replace(i, whole_string):
        whole_string = (whole_string[:i] + new + whole_string[i + len(old):])
        return whole_string

    
    for word in created_words:
        sylls = word.sylls
        
        if skip_stress:
            if len(sylls) < 2:# Skip monosyllabic words
                continue
            stress_syll = stress_remove(word)             
            # Check to see if word.sylls update

        whole_string = ".".join(sylls) # sylls are compiled into string for 
        old_len = len(old)

        i = 0
        while i < len(whole_string):
            # Extracts a substr from whole_string, starting at index i and 
            # extending len(old) characters forward. 
            if whole_string[i:i + len(old)] == old:
                if pre and fol:
                    pre_bool = (match_pre(whole_string, new, old, pre, i))
                    fol_bool = (match_fol(whole_string, new, old, fol, i))
                    if pre_bool and fol_bool: # Match = boolean
                        whole_string = replace(i, whole_string)
            
                elif pre:
                    pre_bool = (match_pre(whole_string, new, old, pre, i))
                    if pre_bool:
                        whole_string = replace(i, whole_string)
                        
                elif fol:
                    fol_bool = match_fol(whole_string, new, old, fol, i)
                    if fol_bool:
                        whole_string = replace(i, whole_string)
                
                else:
                    whole_string = replace(i, whole_string)
            i += 1 # Moves while loop to next character

        if skip_stress: # Reinsterts stressed syll
            whole_string = whole_string.replace("!!!", stress_syll)
        
        word.sylls = whole_string.split(".")


        print(whole_string)




def stress_find (sylls):
    for syllable in sylls:
        if syllable.startswith("ˈ"):
            stress = sylls.index(syllable)
            return stress

def match_fol(whole_string, new, old, fol, i):
    following_match = any(whole_string[i + len(old):i + len(old) + 
                        len(con_fol)] == con_fol for con_fol in fol)
    return following_match     

def match_pre(whole_string, new, old, pre, i):
    # Creates a for loop that cycles through con_pre in pre (list)
    # Extracts substr from whole_string
    # Start at i - len(con) and ending at i (pos where "old" starts)
    preceding_match = any(whole_string[max(0, i - len(con_pre)):i] == con_pre 
                          for con_pre in pre)
    return preceding_match

def stress_remove(word): 
    stress_syll = word.sylls[word.stress] # Stressed syll saved
    word.sylls[word.stress] = "!!!"
    return stress_syll

def main():
    create_words()
    assimilate(cons_by_manner["nasal"], cons_by_manner["plosive"])

if __name__ == '__main__':
    main()


# Figure out how to get user input. 
# Write something to add "." markers to the beginning and end of each pre and fol item entry. 
# Create a function that changes a word based on syllable.
