# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 21:18:39 2023

@author: corentin
"""



import os
import openai




with open(r"G:\Python Github\Python_proj\GPT3_resume_article/data/article_test.txt") as f:
          content = f.readlines()[0]


article = content + "\n\nTl;dr"

openai.api_key ="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"
response = openai.Completion.create(
  model="text-davinci-003",
  prompt=article,
  temperature=0.7,
  max_tokens=160,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=1
)


text_final = response.choices[0].text
