import streamlit as st
import yake
from yake.highlight import TextHighlighter
import pandas as pd
import numpy as np
from PIL import Image 
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import spacy
from spacy import displacy
import re

DEFAULT_TEXT = "GitLab acquires software chat startup Gitter, will open-source the code. GitLab, a startup that provides open source and premium source code repository software that people use to collaborate on software, is announcing today that it has acquired Gitter, a startup that provides chat rooms that are attached to repositories of code so that collaborators can exchange messages. Terms of the deal weren’t disclosed.   Gitter has popped up more and more on GitHub, which is arguably GitLab’s biggest competitor. But Gitter chat rooms are also sprinkled throughout GitLab. For example, a repository for a command-line interface (CLI) for talking on Gitter itself has a Gitter chat room.   GitLab won’t bundle it in its community edition or its enterprise edition yet, but it will open-source the Gitter code for others to build on, GitLab cofounder and CEO Sid Sijbrandij told VentureBeat in an interview. What’s happening now, though, is that as part of GitLab, Gitter is launching a new feature called Topics, where people will be able to ask and answer questions — sort of like Stack Overflow.   'Although Gitter is best in class with indexing things, it’s still sometimes hard to find things,' Sijbrandij said. “In this Q&A product, it’s a lot easier to structure the Q&A. You’re not dealing so much with a chronological timeline where people have different conversations that cross each other. There’s a location for every piece of knowledge, and it can grow over time.”  That technology is already available in beta in Gitter rooms on GitHub, and it will become available on GitLab’s Gitter pages over time, Sijbrandij said.   Gitter launched in 2014, the same year that Slack launched. In October 2015 Gitter announced a $2.2 million funding round. Investors included Index Ventures, Kima Ventures, and Nexus Ventures. Three of Gitter’s six employees are joining GitLab, whose team is remote. Gitter cofounders Mike Bartlett and Andrew Newdigate will remain in London. More than 800,000 developers have registered on Gitter since it launched, and today it has around 300,000 monthly active users.   GitLab announced a $20 million funding round in September. GitLab still offers the Mattermost open source software, which amounts to an alternative to the proprietary Slack app. The startup will continue to recommend Mattermost for internal team communication, a spokesperson told VentureBeat in an email.   Sijbrandij’s blog post on the news is here. Newdigate’s blog post on the news is here.  "
HTML_WRAPPER = """<div style="overflow-x: hidden; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""

st.sidebar.title("YAKE!")
st.sidebar.markdown("""
Extract keywords from sample document
""")
st.sidebar.header('Parameter')

#side bar parameters
x_ngram = st.sidebar.slider("Select max ngram size", 1, 10)
x_dethre = st.sidebar.slider("Select deduplication threshold", 0.5, 1.0)
x_numkeywords = st.sidebar.slider("Select number of keywords to return", 1, 50)
option_algo = st.sidebar.selectbox('deduplication function', ('leve','jaro','seqm'),2)
option_lan = st.sidebar.selectbox( 'Language', ('English','Italian', 'German', 'Dutch', 'Spanish', 'Finnish', 'French', 'Polish', 'Turkish', 'Portuguese', 'Arabic'), 0)

language = option_lan
max_ngram_size = x_ngram
deduplication_thresold = x_dethre
deduplication_algo = option_algo
windowSize = 1
numOfKeywords = x_numkeywords

#User text in content
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
        
#sort the result by ents, as ent rule suggests.
sort_ents = sorted(ents, key=lambda x: x["start"])

st.header('Result')
#use spacy to higlight the keywords
ex = [{"text": text,
       "ents": sort_ents,
       "title": None}]

#st.text(text)
html = displacy.render(ex, style="ent", manual=True)
html = html.replace("\n", " ")
st.write(HTML_WRAPPER.format(html), unsafe_allow_html=True)

#tabular data (columns: keywords, score)
df = pd.DataFrame(keywords, columns=("Keywords by Yake","Keywords Score"))
st.dataframe(df)

# Create and generate a word cloud image:
wordcloud = WordCloud(width = 1000, height = 600, background_color="white", collocations=False, regexp = r"\w[\w ']+").generate(keywords_list)

#Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
st.pyplot()
