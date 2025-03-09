
def contextual_edit(new, old, pre = False, fol = False, skip_stress = False):
    for word in created_words:
        sylls = word.sylls
        
        if skip_stress:
            if len(sylls) < 2:# Skip monosyllabic words
                continue
            stress_remove(word)                                             
            # Check to see if word.sylls updated. 

        whole_string = ".".join(sylls) # sylls are compiled into string for 
        old_len = len(old)

        # Pre and fol cons are converted to a list so multiple values can be searched for.
        if pre:
            pre = pre.split()
        if fol:
            fol = fol.split()     

        i = 0
        while i < len(whole_string):
            # Extracts a substr from whole_string, starting at index i and extending len(old) characters forward. 
            if whole_string[i:i + len(old)] == old:
                if pre and fol:
                    match_pre(whole_string, new, old, pre, i)
                    match_fol(whole_string, new, old, fol, i)              
                    if preceding_match and following_match: # Match variables are booleans
                        whole_string = whole_string[:i] + new + whole_string[i + len(old):]

                elif pre:
                    match_pre(whole_string, new, old, pre, i)
                    if preceding_match:
                        whole_string = whole_string[:i] + new + whole_string[i + len(old):]
                
                elif fol:
                    match_fol(whole_string, new, old, fol, i)
                    if preceding_match:
                        whole_string = whole_string[:i] + new + whole_string[i + len(old):]
                
                else:
                    find_replace(whole_string, new, old)
                    # This may not work --> Check interaction with while loop.
                
            i += 1
        
        if skip_stress:
            stress_insert(whole_string, stress_syll)

        word.sylls = whole_string.split(".")

        return whole_string

def find_replace(whole_string, new, old):
    whole_string = whole_string.replace(new, old)
    return whole_string

def match_fol(whole_string, new, old, fol, i):
    following_match = any(whole_string[i + len(old):i + len(old) + len(con_fol)] == con_fol for con_fol in fol)
    return following_match     

def match_pre(whole_string, new, old, pre, i):
    # Creates a for loop that cycles through con_pre in pre (list)
    # Extracts a substr from whole_string, starting at i - len(con) and ending at i (pos where "old" starts)
    preceding_match = any(whole_string[max(0, i - len(con_pre)):i] == con_pre for con_pre in pre)
    return preceding_match

def stess_insert(whole_string, stress_syll):
    whole_string.replace("!!!.", stress_syll)

def stress_remove(word): 
    stress_syll = word.sylls[word.stress] # Stressed syll saved
    word.sylls[word.stress] = "!!!."
    return stress_syll

    # FUNCTION BEFORE SUBFUNCTIONS
        # i = 0
        # while i < len(whole_string):
        #     # Extracts a substr from whole_string, starting at index i and extending len(old) characters forward. 
        #     if whole_string[i:i + len(old)] == old:
        #         preceding_match = any(whole_string[max(0, i - len(con_pre)):i] == con_pre for con_pre in pre)
        #         following_match = any(whole_string[i + len(old):i + len(old) + len(con_fol)] == con_fol for con_fol in fol)

        #         if preceding_match and following_match:
        #             whole_string = whole_string[:i] + new + whole_string[i + len(old):]
        #     i += 1
        
        # return whole_string



