import ipapy
# vowels are split into three tuples: front, central, back
# vowels within tuples are ordered most open to most closed

vwls_by_posit = {
	"front" : ["a", "ɶ", "æ", "ɛ", "œ", "e̞", "ø̞", "e", "ø", "ɪ", "ʏ",
             "i", "y"], 
	"central" : ["ä", "ɐ", "ɜ", "ɞ", "ə", "ɘ", "ɵ", "ɨ", "ʉ"],
	"back" : ["ɑ", "ɒ", "ʌ", "ɔ", "ɤ̞", "o̞", "ɤ", "o", "ʊ", "ɯ", "u"]
}

user_input = [
	["maŋ", "nʊs̠", "adj_nom_sing"], ["ka", "nɪs", "n_nom_sing"], 
	["feː", "leːm", "n_acc_sing"], ["par", "wam", "adj_acc_sing"], 
	["mɔr", "dɛt", "verb"]]


class Word: 
	def __init__(self, syn_func, sylls)
		self.syn_func = syn_func
		self.sylls = sylls
	def __repr__(self):
		return f"{self.syn_func}"

def obj_creator(): 
	for word in user_words:
		word[-1] == 

def joiner(word):
	joined = ">".join(word)
	return joined

# THIS NEEDS WORK - SHOULD BE ABLE TO FIND CLUSTERS
def add_first(new, find_con):
	for word in user_input:
		if word[0].startswith(find_con):
			word.insert[0, new]
			print(word)

def add_last(new, find_con):
	for word in user_input:
		if word[-1].endswith(find_con):
			word.append[new]

def add_affix(new, new_loc, find_con, find_pos, skip_stress):
	# Con_list takes the find_con string and turns it into a list.
	con_list = con_list.append(find_con.split)

	for word in user_input:
		if find_pos == "last" and word[find_pos].endswith(any(find_con)):
			insert
		if not skip_stress:
			new_list = new_list.append("ˈ" + new)

def insert()
	...

# Works for: deletions (aphaersis, apocope),
def replace_char(old, new, fixed_syll, skip_stress):
	for word in user_input:
		if fixed_syll:
			word[fixed_syll].replace(new,old)
		else: 
		    for syllable in word:
			    if old in syllable:
				    syllable = syllable.replace(old, new)



# Works for: intervoc spir/voicing, syncop
# def inter_char(new, old):
# 	for word in quote:
# 		joiner(word)
# 		split = list(joined)
		
# 		for char in range(1, len(split) - 1):
# 			if split[char -1] in [vowels.front, vowels.central, vowels.back] and 
				
			

add_affix(1, 1, "ɛ̃", -1)

