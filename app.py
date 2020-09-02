import streamlit as st
import yake
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy
from spacy import displacy
import re
from bidi.algorithm import get_display

HTML_WRAPPER = """<div style="overflow-x: hidden; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""

st.sidebar.title("YAKE!")
st.sidebar.markdown("""
Extract keywords from sample document
""")
st.sidebar.header('Parameter')

#side bar parameters
x_ngram = st.sidebar.slider("Select max ngram size", 1, 10, 3)
x_dethre = st.sidebar.slider("Select deduplication threshold", 0.5, 1.0, 0.9)
x_numkeywords = st.sidebar.slider("Select number of keywords to return", 1, 50, 20)
option_algo = st.sidebar.selectbox('deduplication function', ('leve','jaro','seqm'),2)
option_lan = st.sidebar.selectbox( 'Language', ('English','Italian', 'German', 'Dutch', 'Spanish', 'Finnish', 'French', 'Polish', 'Turkish', 'Portuguese', 'Arabic'), 0)

language = option_lan
max_ngram_size = x_ngram
deduplication_thresold = x_dethre
deduplication_algo = option_algo
windowSize = 1
numOfKeywords = x_numkeywords

#User text in content
file = open(str(option_lan) + ".txt")
DEFAULT_TEXT  = file.read()
file.close()

st.header('Content')
text = st.text_area("Please input the content", DEFAULT_TEXT, 330)

#use yake to extract keywords
custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
keywords = custom_kw_extractor.extract_keywords(text)

#get keywords and their position
ents = []

text_lower = text.lower()

keywords_list = str(keywords[0][0])
for m in re.finditer(keywords_list, text_lower): 
    d = dict(start = m.start(), end = m.end(), label = "")
    ents.append(d)
    
for i in range(1, len(keywords)):
    kwords = str(keywords[i][0])
    keywords_list += (', ' + kwords)
    for m in re.finditer(kwords, text_lower): 
        d = dict(start = m.start(), end = m.end(), label = "")
        ents.append(d)
      
#sort the result by ents, as ent rule suggests
sort_ents = sorted(ents, key=lambda x: x["start"])

st.header('Result')
#use spacy to higlight the keywords
ex = [{"text": text,
       "ents": sort_ents,
       "title": None}]

html = displacy.render(ex, style="ent", manual=True)
html = html.replace("\n", " ")
st.write(HTML_WRAPPER.format(html), unsafe_allow_html=True)

#tabular data (columns: keywords, score)
df = pd.DataFrame(keywords, columns=("Keywords Score", "Keywords by Yake"))
l=[1,0]
df = df[[df.columns[i] for i in l]]
st.dataframe(df)

#create and generate a word cloud image:
bidi_text = get_display(keywords_list)
wordcloud = WordCloud(width = 1000, height = 600, background_color="white", collocations=False, regexp = r"\w[\w ']+", font_path='tradbdo.ttf').generate(keywords_list)

#display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
st.pyplot()
