import nltk
from nltk import word_tokenize
from nltk.tag.stanford import NERTagger

st = NERTagger('stanford-ner/all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')
sentence = "Ping Pong almost cracking the top 20. Nice. Too bad its characters, aka the best part of the show, can't get into any of the contest brackets..."
tokens = word_tokenize(sentence)
tokens = nltk.pos_tag(tokens)

#for x in tokens:
#	print(x)
#	if x[1] == 'NNP':
#		print(x)

for sent in nltk.sent_tokenize(sentence):
    tokens = nltk.tokenize.word_tokenize(sent)
    tags = st.tag(tokens)
    for tag in tags:
        if tag[1]=='PERSON': print(tag)