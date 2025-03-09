import ipapy
clause = {}
user_words = []

class Declension:

	#  Declension lists do not include nom_sing, they are default in syllables.

	def __init__(self, name, nom_sing, nom_plur, gen_sing, gen_plur, dat_sing, dat_plur, 
			    acc_sing, acc_plur, abl_sing, abl_plur, voc_sing, voc_plur, 
				loc_sing, loc_plur):
		
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
		self.loc_sing = loc_sing
		self.loc_plur = loc_plur

class Word:                                  
    def __init__(self, name, classification, inflection, modifier, 
                syn_function, syllables):
        self.name = name
        self.classification = classification
        self.inflection = inflection
        self.modifier = modifier
        self.syn_function = syn_function
        self.syllables = syllables

    def __repr__(self):
        return f"{self.name}"
	
base_words = {
## NOUNS
	"dog" : Word("dog", "masc", "third_um", "", "undef", ["ka", "nɪs"]),
	"cat" : Word("cat", "fem", "third_ium", "", "undef", ["feː", "leːs"]),
	"lion" : Word("lion", "masc", "third_um", "+n", "undef", ["lɛ", "oː"]),
	"horse" : Word("horse", "masc", "second", "", "undef", ["ɛk", "ʊs̠"]),
	"big" : Word("big", "adj", "primary", "", "undef", ["maŋ", "nʊs̠"]),
    "small" : Word("small_", "adj", "primary", "", "undef", 
				["par", "wʊs̠"]),
	"sacred" : Word("sacred", "adj", "primary", "ɛr>r", "undef", ["sa", "kɛr"])
}

decs_adj = {
	"primary_masc": Declension("primary_masc",
		"ʊs", "iː", "iː", "oː.rʊm", "oː", "iːs",
		"ʊm", "oːs", "oː", "iːs", "ɛ", "iː", "iː", "iːs"),

	"primary_fem": Declension("primary_fem",
		"a", "ae", "ae", "aː.rʊm", "ae", "iːs",
		"am", "aːs", "aː", "iːs", "a", "ae", "ae", "iːs"),

	"primary_neu": Declension("primary_neu",
		"ʊm", "a", "iː", "oː.rʊm", "oː", "iːs",
		"ʊm", "a", "oː", "iːs", "ʊm", "aː", "iː", "iːs"),

}

decs_noun = {
	# nom_sing entry is a list of endings the decliner will search and replace
	# nom_sing entries should never have to be pulled and used.

## FIRST DECLENSION PARADIGM

    "first": Declension("first",
        ["a"], "ae", "ae", "aː.rʊm", "ae", "iːs", 
        "am", "aːs", "aː", "iːs", "a", "ae", "ae", "iːs"),

## SECOND DECLENSION PARADIGMS

    "second_masc": Declension("second_masc",
        ["ɛr", "ʊs"], "iː", "iː", "oː.rʊm", "oː", "iːs", 
		"ʊm", "oːs", "oː", "iːs", "ɛ", "iː", "iː", "iːs"),

    "second_neu": Declension("second_neu",
        ["ʊm"], "a", "ɪ", "oː.rʊm", "oː", "iːs", 
        "ʊm", "a", "oː", "iːs", "ʊm", "a", "iː", "iːs"),

# THIRD DECLENSION PARADIGMS
# The first two paradigms are both masc but differ in the genitive plural
    "third_um": Declension("third_um",
        ["eːs", "ɪs", "ʊs"], "eːs", "ɪs", "ʊm", "iː", "ɪ.bʊs", 
        "ɛm", "eːs", "ɛ", "ɪ.bʊs", "eːs", "eːs", "iː", "ɪ.bʊs"),

    "third_ium": Declension("third_ium",
        ["eːs", "ɪs"], "eːs", "ɪs", "iʊm", "iː", "ɪ.bʊs", 
        "ɛm", "eːs", "ɛ", "ɪ.bʊs", "eːs", "eːs", "iː", "ɪ.bʊs"),	

    "third_neu_um": Declension("third_neu_um",
        [""], "a", "ɪs", "ʊm", "iː", "ɪ.bʊs", 
        "", "a", "ɛ", "ɪ.bʊs", "", "a", "iː", "ɪ.bʊs"),	

    "third_neu_ium": Declension("third_neu_ium",
        [""], "ia", "ɪs", "iʊm", "iː", "ɪ.bʊs", 
        "", "ia", "iː", "ɪ.bʊs", "", "ia", "iː", "ɪ.bʊs"),	

# FOURTH DECLENSION PARADIGMS
    "fourth_masc": Declension("fourth_masc",
        ["ʊs"], "uːs", "uːs", "u.um", "uiː", "ɪ.bʊs",
        "ʊm", "uːs", "uː", "ɪ.bʊs", "ʊs", "uːs", "iː", "ɪ.bʊs"),
    
    "fourth_neu": Declension("fourth_neu",
        ["uː"], "ua", "uːs", "u.um", "uː", "ɪ.bʊs",
        "uː", "uːa", "uː", "ɪ.bʊs", "uː", "uːa","iː", "ɪ.bʊs"),

# FIFTH DECLENSION PARADIGM
    "fifth": Declension("fifth",
        "eːs", "eːs", "eː.iː", "eːrʊm", "eː.iː", "eː.bʊs",
        "ɛm", "eːs", "eː", "eːbʊs", "eːs", "eːs", "eː", "eːbʊs")
}

# if syn_function != "nom_sing" or (= "voc_sing":

def main():
	get_user_words(user_words)
	create_words(base_words, user_words)
	inflect_word(clause)

	for entry in clause.values():
		print(entry.syllables)

def con_adj(word):
	


	decline_word()

def con_noun(word):
	inflection = word.inflection
	syllables = word.syllables
	syn_function = word.syn_function

	if syn_function == "nom_sing" or (syn_function == "voc_sing" and inflection != "second"):
		return
	# Skips decliner as nom_sing is the default; same w/ voc_sing in second dec
	
	for decs in decs_noun:
		if decs == inflection:
			decs = decs_noun[decs]
			new_inf = getattr(decs, syn_function)

			decline_word(decs, new_inf, syllables, word)
			break

def create_words(base_words, user_words):
	user_words.reverse() # Reverses word order so adj knows noun to modify
	
	for entry in user_words:
		base = base_words[entry[0]]

		if len(entry) > 1 : base.syn_function = entry[1]
		# Adds syn_function if user difined one.
		# Useful for adverbs, adjectives create from nouns, and all nouns.

		if base.classification == "adj":
			base.classification = last_word[0]
			base.syn_function = "adj>" + last_word[1]
		# Changes adj class and syn_func to match preceding noun

		clause[base.syn_function] = base
		last_word = [base.classification, base.syn_function]
	
def decline_word(decs, new_inf, syllables, word):
	modify_word(syllables, word)

	for old_inf in decs.nom_sing:
		if old_inf in syllables[-1]:
			syllables[-1] = syllables[-1].replace(old_inf, new_inf)
			break
		else:
			syllables[-1] = syllables[-1] + new_inf
			break
	# Accesses a list of nom_sing endings in the declension
		# Looks to see if any nom_sing endings are present in last syllable
			# Replaces nom_sing with the new_inf
	
	 ## SPLIT MULTISYLLABIC INFLECTIONS 

	if "." in syllables[-1]:
		split_syll = syllables[-1].split(".")
		syllables.pop()
		syllables.extend(split_syll)

def inflect_word(clause):
	for entry in clause:
		word = clause[entry]

		if "adj" in word.syn_function:
			con_adj (word)
		elif word.classification in ["masc", "fem", "neu"]:
			con_noun(word)

def get_user_words(user_words):
	user_input = input("Translate: ").split()
	for entry in user_input:
		user_words.append(entry.split(">"))

	
	for entry in user_words:
		if len(entry) > 1: 
			while True:
				if entry[1] in [
				"nom_sing", "nom_plur", "gen_sing", "gen_plur",
				"dat_sing", "dat_plur", "acc_sing", "acc_plur",
				"abl_sing", "able_plur", "voc_sing", "voc_plur",
				"loc_sing", "loc_plur"]:
					break
				else:
					print(f"{entry[1]} is not a valid syntactic function.")
					entry[1] = input("Please try again: ")

def modify_word(syllables, word):
		mod = word.modifier
		if "+" in mod:
			syllables = syllables.append(mod.replace("+", ""))

		if ">" in mod:
			chars = mod.split(">")
			syllables[-1] = syllables[-1].replace(chars[0], chars[1])
		# Replces one char for another, typically for consonant change

main()