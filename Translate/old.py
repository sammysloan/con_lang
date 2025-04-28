import ipapy

## The base_words are divided up thusly:
    ## ENGLISH NAME
    ## CLASSIFICATION - the default class/distinction
    ##   Parts can be overriden in input to create adverbs, noun-adj, etc.
    ## INFLECTION - decs for adj + nouns, conj for verbs
    ## SYLLABLES

base_words = [
    ["dog_", "masc", "third_is", "ka", "nɪs̠"], 
    ["cat_", "fem", "third_es", "feː", "leːs"],
    ["wolf_", "masc", "second_us", "lʊ", "pʊs"],
    ["lion_", "masc", "third_^n", "le", "oː"],
    ["big_", "adj_undef", "adj_first_sec", "maŋ", "nʊs̠"],
    ["small_", "adj_undef", "adj_first_sec", "par", "wʊs̠"],
    ["thick_", "adj_undef", "adj_first_sec", "kras̠", "s̠ʊs̠"],
    ["thin_", "adj_undef", "adj_third", "t̪ɛ", "nʊ", "is̠"],
    ["bite_", "adj", "conj", "mɔr", "d̪e", "ɔː"],
    ["king_", "masc", "third_xg", "rex"],
    ["torpor_", "masc", "third_or", "tɔr", "pɔr"],
    ["enemy_", "masc", "third_is", "hɔs", "tɪs"],
    ["hand_", "fem", "fourth_masc_fem", "ma", "nʊs"],
    ["series_", "fem", "fifth_", "s̠ɛ", "ri", "eːs"],
]

created_words = {}
user_words = []

class Declension:
    def __init__(self, name, nom_sing, nom_plur, gen_sing, gen_plur, 
                 dat_sing, dat_plur, acc_sing, acc_plur, abl_sing, abl_plur,
                voc_sing, voc_plur):
        self.name = name
        self.nom_sing = nom_sing
        self.nom_plur = nom_plur
        self.gen_sing = gen_sing
        self.gen_plur = gen_plur
        self.dat_sing = dat_sing
        self.dat_plur = dat_plur
        self.acc_sing = acc_sing
        self.acc_plur = acc_plur
        self.abl_sing = abl_sing
        self.abl_plur = abl_plur
        self.voc_sing = voc_sing
        self.voc_plur = voc_plur
    
    def __repr__(self):
        return f"{self.name}"
        

class Word:                                  
    def __init__(self, name, classification, inflection, syn_function, syllables):
        self.name = name
        self.classification = classification
        self.syn_function = syn_function
        self.inflection = inflection
        self.syllables = syllables

    def __repr__(self):
        return f"{self.syn_function}"
    

dec_dict = {
## FIRST DECLENSION PARADIGM

    "first": Declension("first",
        "a", "ae̯", "ae̯", "aː.rʊm", "ae̯", "iːs", 
        "am", "aːs", "aː", "iːs", "a", "ae̯"),

## SECOND DECLENSION PARADIGMS

    "second_er": Declension("second_er",
        "ɛr", "ɪ", "oː.rʊm", "ɔ", "iːs", "ʊm", 
        "oːs", "ɔ", "iːs", "ɛr", "iːs", "a"),

    "second_um": Declension("second_um",
        "ʊm", "a", "ɪ", "oː.rʊm", "ɔ", "iːs", 
        "ʊm", "a", "ɔ", "iːs", "ʊm", "a"),

    "second_us": Declension("second_us",
        "ʊs", "ɪ", "ɪ", "oː.rʊm", "ɔ", "iːs", 
        "ʊm", "oːs", "ɔ", "iːs", "ɛ", "iːs"),


## M/F THIRD DECLENSION PARADIGMS

    "third_es": Declension("third_es",
        "eːs", "eːs", "ɪs", "ium", "iː", "ɪ.bʊs", 
        "ɛm", "eːs", "ɛ", "ɪ.bʊs", "eːs", "eːs"),
    
    "third_is": Declension("third_is",
        "ɪs", "eːs", "ɪs", "um", "iː", "ɪ.bʊs", 
        "ɛm", "eːs", "ɛ", "ɪ.bʊs", "ɪs", "eːs"),

    "third_or": Declension("third_or",
        "or", "oːr.eːs", "oːr.ɪs", "oːr.ʊm", "oːr.iː", "oːr.ɪ.bʊs", 
        "oːr.ɛm", "oːr.eːs", "oːr.ɛ", "oːr.ɪ.bʊs", "ɔr", "oːr.eːs"),

    "third_es^it": Declension("third_es^it",
        "ɛs", "ɪteːs", "ɪt.ɪs", "ɪt.iʊm", "ɪt.iː", "ɪt.ɪ.bʊs", 
        "ɪt.ɛm", "ɪt.eːs", "ɪt.ɛ", "ɪt.ɪ.bʊs", "ɛs", "ɪt.eːs"),

    "third_o^in": Declension("third_o^in",
        "oː", "ɪneːs", "ɪn.ɪs", "ɪn.ʊm", "ɪn.iː", "ɪn.ɪ.bʊs", 
        "ɪn.ɛm", "ɪn.eːs", "ɪn.ɛ", "ɪn.ɪ.bʊs", "oː", "ɪn.eːs"),

    "third_s^b": Declension("third_s^b",
        "s", "beːs", "b.ɪs", "b.iʊm", "b.iː", "b.ɪ.bʊs", 
        "b.ɛm", "b.eːs", "b.ɛ", "b.ɪ.bʊs", "s", "b.eːs"),

    "third_s^d": Declension("third_s^d",
        "s", "deːs", "d.ɪs", "d.ʊm", "d.iː", "d.ɪ.bʊs", 
        "d.ɛm", "d.eːs", "d.ɛ", "d.ɪ.bʊs", "s", "d.eːs"),

    "third_s^t": Declension("third_s^t",
        "s", "teːs", "t.ɪs", "t.ʊm", "t.iː", "t.ɪ.bʊs", 
        "t.ɛm", "t.eːs", "t.ɛ", "t.ɪ.bʊs", "s", "t.eːs"),

    "third_x^c": Declension("third_x^c",
        "x", ".ɡeːs", ".cɪs", ".cʊm", ".ciː", ".cɪ.bʊs", 
        ".cɛm", ".ceːs", ".cɛ", ".cɪ.bʊs", "x", "ceːs"),

    "third_x^g": Declension("third_x^g",
        "x", ".ɡeːs", ".gɪs", ".gʊm", ".ɡiː", ".ɡɪ.bʊs", 
        ".gɛm", ".geːs", ".gɛ", ".gɪ.bʊs", "x", ".ɡeːs"),
    
    "third_^n": Declension("third_^n",
        "", "neːs", "nɪs", "nʊm", "niː", "nɪ.bʊs", 
        "nɛm", "neːs", "nɛ", "nɪ.bʊs", "", "neːs"),

## NUETER THIRD DECLENSION PARADIGMS
    "third_en": Declension("third_en", 
        "ɛn", "ɪ.na", "ɪ.nɪs","ɪ.nʊm", "ɪ.niː", "ɪ.nɪ.bʊs",
        "ɛn", "ɪ.na", "ɪ.nɛ", "ɪ.nɪ.bʊs", "ɛn", "ɪ.na"),

    "third_ut": Declension("third_ut", 
        "ʊt", "ɪ.ta", "ɪ.tɪs","ɪ.tʊm", "ɪ.tiː", "ɪ.tɪ.bʊs",
        "ʊt", "ɪ.ta", "ɪ.tɛ", "ɪ.tɪ.bʊs", "ʊt", "ɪ.ta"),

    "third_us^or": Declension("third_us^or", 
        "ʊs", "ɔr.a", "ɔr.ɪs","ɔr.ʊm", "ɔr.iː", "ɔr.ɪ.bʊs",
        "ʊs", "ɔr.a", "ɔr.ɛ", "ɔr.ɪ.bʊs", "ʊs", "ɔr.a"),

    "third_us^er": Declension("third_us^er", 
        "ʊs", "ɛr.a", "ɛr.ɪs","ɛr.ʊm", "ɛr.iː", "ɛr.ɪ.bʊs",
        "ʊs", "ɛr.a", "ɛr.ɛ", "ɛr.ɪ.bʊs", "ʊs", "ɛr.a"),

    "third_^d": Declension("third_d", 
        "", "da", "dɪs","dʊm", "diː", "dɪ.bʊs",
        "", "da", "dɛ", "dɪ.bʊs", "", "da"),

## FOURTH DECLENSION PARADIGMS

    "fourth_masc_fem": Declension("fourth_masc_fem",
        "ʊs", "uːs", "uːs", "uːm", "uiː", "ɪ.bʊs",
        "ʊm", "uːs", "uː", "ɪ.bʊs", "ʊs", "uːs"),
    
    "fourth_nueter": Declension("fourth_nueter",
        "uː", "ua", "uːs", "uːm", "uiː", "ɪ.bʊs",
        "ʊm", "uːs", "uː", "ɪ.bʊs", "ʊs", "uːs"),

## FIFTH DECLENSION PARADIGM

    "fifth": Declension("fifth",
        "eːs", "eːs", "eː.iː", "eːrʊm", "eː.iː", "eː.bʊs",
        "ɛm", "eːs", "eː", "eːbʊs", "eːs", "eːs"),
}

## ADJECTIVAL DECLENSION PARADIGMS
adj_decs = {
    "adj_fs_us" : {
        "masc": Declension("masc",
            "ʊs", "iː", "iː", "oːr.ʊm", "oː", "iːs",
            "ʊm", "oːs", "oː", "iːs", "ɛ", "ɛ"),
        
        "fem": Declension("fem",
            "a", "ae", "ae̯", "aːr.ʊm", "ae", "iːs",
            "ʊm", "aːs", "oː", "iːs", "a", "ae"),
        
        "neu": Declension("neu",
            "ʊm", "a", "iː", "oːr.ʊm", "oː", "iːs",
            "ʊm", "a", "oː", "iːs", "ʊm", "a"),
    },

   "adj_fs_us^ius" : {
       "masc": Declension("masc",
           "ʊs", "iː", "iːʊs", "oːr.ʊm", "iː", "iːs",
           "ʊm", "oːs", "oː", "iːs", "ɛ", "iː"),
      
       "fem": Declension("fem",
           "a", "ae", "iːʊs", "aːr.ʊm", "iː", "iːs",
           "am", "aːs", "aː", "iːs", "a", "ae"),
      
       "neu": Declension("neu",
           "ʊm", "a", "iːʊs", "oːr.ʊm", "iː", "iːs",
           "ʊm", "a", "aː", "iːs", "ʊm", "a"),
   },

   "adj_fs_er^ius" : {
       "masc": Declension("masc",
           "", "iː", "iːʊs", "oːr.ʊm", "iː", "iːs",
           "ʊm", "oːs", "oː", "iːs", "", "iː"),
      
       "fem": Declension("fem",
           "a", "ae", "iːʊs", "aːr.ʊm", "iː", "iːs",
           "am", "aːs", "aː", "iːs", "a", "ae"),
      
       "neu": Declension("neu",
           "ʊm", "a", "iːʊs", "oːr.ʊm", "iː", "iːs",
           "ʊm", "a", "oː", "iːs", "ʊm", "a"),
   },




    "adj_third" : {
        "masc": Declension("masc",
            "eːns", "ɛn.teːs", "ɛn.tɪs", "ɛn.ti.ʊm", "ɛn.tiː", "ɛn.tiː.bʊs",
            "ɛn.tɛm", "ɛn.teːs", "ɛn.tiː", "ɛn.tiː.bʊs", "eːns", "ɛn.teːs"),

        "fem": Declension("fem",
            "eːns", "ɛn.teːs", "ɛn.tɪs", "ɛn.ti.ʊm", "ɛn.tiː", "ɛn.tiː.bʊs",
            "ɛn.tɛm", "ɛn.teːs", "ɛn.tiː", "ɛn.tiː.bʊs", "eːns", "ɛn.teːs"),

        "third_neu": Declension("third_neu",
            "eːns", "ɛn.ti.a", "ɛn.tɪs", "ɛn.ti.ʊm", "ɛn.tiː", "ɛn.tiː.bʊs",
            "eːns", "ɛn.ti.a", "ɛn.tiː", "ɛn.tiː.bʊs", "eːns", "ɛn.ti.a"),
    }
}

irregular_declensions = {...}

pronoun_declensions = {
    "first_person": Declension("first_person",
    "ɛɡɔ", "noːs̠", "meiː", "nɔs̠t̪riː", "mi(ɦ)iː", "noːbiːs̠",
    "meː", "noːs̠", "meː", "noːbiːs̠", "ɛɡɔ", "noːs̠"),
}

def main():
    deliniator(user_words)
    create_words(base_words, user_words)
    inflector(created_words, dec_dict)


def create_words(base_words, user_words):
    user_words.reverse()
    key_list = []
    for entry in user_words:
        for base in base_words:
            if base[0] == entry[0] + "_":
                name = entry[0]
                classification = base[1]
                inflection = base[2]
                syllables = base[3:]

                if len(entry) > 1 : syn_function = entry[1]

                if classification == "adj_undef":
                    syn_function = "adj>" + key_list[-1].syn_function
                    classification = key_list[-1].classification

                this_word = Word(name, classification, inflection, 
                                syn_function, syllables)
                created_words[syn_function] = this_word
                key_list.append(this_word)
                break

## SHOULD GENDER BE ADDED TO THE ADJECTIVE HERE OR LATER???

def con_adj(adj_decs, word):
    inflection = word.inflection
    gender = word.classification
    syn_function = word.syn_function.replace("adj>", "")
    syllables = word.syllables

    for decs in adj_decs[inflection]:
        if decs == gender: 
            decs = adj_decs[inflection][gender]
            new_inf = getattr(decs, syn_function)
            break
    
    decliner(decs, new_inf, syllables)

def con_adv():
    ...

def con_n(dec_dict, word):
    inflection =  word.inflection
    syllables = word.syllables
    syn_function = word.syn_function

## Adding irregularity check here won't work, because it will have already
## vetted by the inflector --> IT SHOULD BE ADDED THERE

## SEARCH FOR DECLENSION ENDING
    for decs in dec_dict:
        if decs == inflection:
            decs = dec_dict[decs]
            new_inf = getattr(decs, syn_function)
            
            decliner(decs, new_inf, syllables)
            break

# ## EDIT WORD TO INCLUDE NEW DECLENSION ENDING
#     if not decs.nom_sing:
#         syllables.append(new_inf)
#     else:
#         if new_inf in syllables[-1]:
#             pass
#         else:
#             old_inf = decs.nom_sing
#             syllables[-1] = syllables[-1].replace(old_inf, new_inf)


 ## SPLIT MULTISYLLABIC INFLECTIONS 
    if "." in syllables[-1]:
        split_syll = syllables[-1].split(".")
        syllables.pop()
        syllables.extend(split_syll)

    print(syllables)

    
def con_p():
    ...

def con_v():
    ...

def decliner(decs, new_inf, syllables):

## EDIT WORD TO INCLUDE NEW DECLENSION ENDING
    if not decs.nom_sing:
        syllables.append(new_inf)
    else:
        if new_inf in syllables[-1]:
            pass
        else:
            old_inf = decs.nom_sing
            syllables[-1] = syllables[-1].replace(old_inf, new_inf)


 ## SPLIT MULTISYLLABIC INFLECTIONS 
    if "." in syllables[-1]:
        split_syll = syllables[-1].split(".")
        syllables.pop()
        syllables.extend(split_syll)

    print(syllables)

def deliniator(user_words):
    u_input = input("Translate: ").split()
    for entry in u_input:
        user_words.append(entry.split(">"))
    return(user_words)

def inflector(created_words, dec_dict):
    for entry in created_words:
        word = created_words[entry]
        if "adj" in word.syn_function:
            con_adj(adj_decs, word)
        elif word.syn_function == "adv":
            con_adv()
        elif word.syn_function in ["abl_sing", "abl_plur", "acc_sing", 
        "acc_plur", "dat_sing", "dat_plur", "gen_sing", "gen_plur", "loc_sing",
        "loc_plur", "nom_sing", "nom_plur"]:
            con_n(dec_dict, word)
        elif word.syn_function == "p":
            con_p()
        elif word.syn_function  == "v":
            con_v()



    


## Verb aspect, mood, etc. is defined within the UI - verb/noun agreement are 
## encoded within the syn_function 


## Compiler may want to reverse the user_list in order to ensure the adjectives
## properly correspond with the noun the modify.

            # if entry[1] == "adj":
            #     con_adj()
            # elif entry[1] == "adv":
            #     con_adv()
            # elif entry[1] == ["abl", "acc", "dat", "gen", "loc", "nom"]:
            #     con_n()
            # elif entry [1] == "v":
            #     con_v()
    
main()