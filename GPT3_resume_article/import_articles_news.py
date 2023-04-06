# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 19:17:37 2023

@author: corentin
"""


from newsapi import NewsApiClient
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4.element import Tag
import matplotlib.pyplot as plt

# Init
newsapi = NewsApiClient(api_key='da52d31a65a84f2296c46f88038d6c41')

# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(#q='Crypto',
                                          #language="en",
                                          #category="general",
                                          sources='bbc-news,reuters,le-monde,The Guardian,financial-times',
                                          page_size=100
                                          )
                                          
dict_article_url={}
i=0
for d in top_headlines["articles"] :
    
    
    title=d["title"]
    url=d["url"]
    source =d["source"]["name"]
    date = d["publishedAt"]
    start=d["content"]
    
    dict_article_url[f"article_{i}"]={
        "title":title,
        "source":source,
        "date":date,
        "url":url,
        "article_start":start
        }
    i+=1

article_dict=dict_article_url["article_9"]

#response = requests.get(article_t["url"])
#html = urlopen(article_t["url"]).read()

for s in dict_article_url:
    print(dict_article_url[s]["source"])

def get_article_content(article_dict):
    
    remove_words_share=["facebook","twitter","whatsapp","reddit"]
    remove_words=["email","advertisement"]
    
    html = urlopen(article_dict["url"]).read()
    tree = BeautifulSoup(html,"lxml")

    body = tree.body

    for tag in body.select('script'):
        tag.decompose()
    for tag in body.select('style'):
        tag.decompose()

    text = body.get_text(separator='\n')

    lines = text.split("\n")
    lines=["start"]+lines

    start_line=0
    end_line=0

    #sum_charac=sum([len(l) for l in lines])
    nb_w =[len(l.split(" ")) for l in lines]
    
    for i in range(len(lines)):
        l=lines[i]
        if start_line==0:
            if len(l)>80 and l!=article_dict["title"]: #more than 80 characters in the line and not the title
                #if i+1<len(lines) and (len(lines[i+1].split(" "))>=5 or len(lines[i+1])<=3): #make sure the lines after is not the end ( assume than an article is compose of more than one paragraph)
                    start_line=i 
    
    for i in range(len(lines)-1,start_line,-1):
        
        if nb_w[i]>9 and (nb_w[i-1]>9 or nb_w[i-2]>9) and lines[i].rstrip()[-1] in [".","?","!"]:
            end_line=i
            break
    end_line_init=end_line+0
    if lines[end_line].rstrip()[-1] not in [".","?","!"]:
        while lines[end_line][-1].rstrip() not in [".","?","!"] and end_line>start_line:
            end_line-=1
        # end_line+=1
        
    if  ( (lines[start_line][-1] not in [".","?","!"]) or (lines[start_line+1][0]!=" " and lines[start_line][-1].isalpha()) ):
        while  ( (lines[start_line][-1] not in [".","?","!"]) or (lines[start_line+1][0]!=" " and lines[start_line][-1].isalpha()) ):
            start_line+=1
            
    elif lines[start_line][0].isupper()==False:
        while lines[start_line][0].isupper()==False:
            start_line-=1
    # for i in range(len(lines)):
    #     l=lines[i]
    #     if start_line==0:
    #         if len(l.split(" "))>5 and l!=article_dict["title"]: #more than 5 words in the line and not the title
    #             if i+1<len(lines) and (len(lines[i+1].split(" "))>=5 or len(lines[i+1])<=3): #make sure the lines after is not the end ( assume than an article is compose of more than one paragraph)
    #                 start_line=i
    #     else:
    #         if len(l.split(" "))<5 and len(l.split(" "))>1: #les than 5 words but more than 2 characters
    #             end_line=i
    #             break
                
    lines_filter=lines[start_line:end_line+1]
    # lines_filter=[l for l in lines_filter if len(l.split(" "))>1 or len(l)<3]
    
    clean_lines=[]
    for l in lines_filter:
        #l=lines_filter[1]
        if len(l.split(" "))>4:
            clean_lines.append(l)
            
        elif any([w.lower() in remove_words_share for w in l.split(" ")])==True and "share" in l.lower().split(" "):
            continue
        elif any([w.lower() in remove_words for w in l.split(" ")]):
            continue
        else:
            clean_lines.append(l)
        # not( ((any([w.lower() in remove_words_share for w in l]) and "share" in l.lower()) or any([w.lower() in remove_words for w in l])) and len(l.split(" "))<5 ) :
        #     clean_lines.append(l)
    text_article = " ".join(lines_filter)
    
    if "blocking" in text_article and len(text_article.rstrip())<75:
        text_article="error from scrap blocking"
    elif len(text_article.rstrip())<75:
        text_article="error, article not enough long"
    return text_article

for a in dict_article_url:

    try:
        dict_article_url[a]["text"]=get_article_content(dict_article_url[a])
    except:
        dict_article_url[a]["text"]="error"

# text_exemple = dict_article_url["article_1"]["text"]

# text_file = open(r"G:\Python Github\Python_proj\GPT3_resume_article/data/article_test.txt","w")
# text_file.write(text_exemple)
# text_file.close()

import os
import openai

openai.api_key ="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"

dict_summary_news={}

for a in dict_article_url:
    
    article = dict_article_url[a]
    
    title = article["title"]
    content = article["text"]
    
    promt = title + " \n "+ content + "\n\nTl;dr"
    
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=promt,
      temperature=0.75,
      max_tokens=180,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=1
    )
    
    text_final = response.choices[0].text
    
    article_end = {
        "title":title,
        "summary":text_final,
        "source":article["source"],
        "date":article["date"],
        "based_text" : content
        
        }
    
    dict_summary_news[a]=article_end
    
message ="\n\n"

for article in dict_summary_news:
    
    message += dict_summary_news[article]["title"]+"\n"+dict_summary_news[article]["source"]+ f": {dict_article_url[article]['url']}"+"\n\n"
    message += dict_summary_news[article]["summary"]+"\n\n\n"
   
subject = "Daily news summarise by an AI"

message_email=f"Subject: {subject}"+message
#message_email = message.encode('utf-8').strip()
    
import smtplib

# Create an instance of the SMTP class
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()


sender_email = "corentinbourdeix@gmail.com"
password = "kckdialwanutwgso"

# Login to the email server (if required)
server.login(sender_email, password)

receiver_email = "c.bourdeix@orange.fr"
receiver_email = "corentin.bourdeix@juliusbaer.com"



message_email = message_email.encode('utf-8').strip()

server.sendmail(sender_email, receiver_email, message_email)



















