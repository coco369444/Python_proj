# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 21:10:37 2022

@author: corentin
"""
import pandas as pd
import numpy as np
import datetime
import seaborn as sns

import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#path_source = r"C:\Users\cbour\OneDrive\Bureau\Python proj\Python_proj\bank account management\data"
path_source = r"G:\Python Github\Python_proj\bank account management\data"



def create_fig(currency,banks,normalized=False,nb_month=6): 
    def rgb_to_hex(rgb):
      c = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
      return f"rgb{c}"
  
    food_palette=[rgb_to_hex(c) for c in  sns.color_palette("Blues", 8)[3:]]
    inc_money_pal = [rgb_to_hex(c) for c in  sns.color_palette("Greens", 10)[3:]]
    service_pal = [rgb_to_hex(c) for c in  sns.color_palette("Oranges", 12)[3:]]
    shopping_pal = [rgb_to_hex(c) for c in  sns.color_palette("RdPu", 9)[3:]]
    
        
    color_discrete_map={
            'alimentation': food_palette[0],
            'Salary': inc_money_pal[0],
            'games': shopping_pal[0],
            'transport': service_pal[0],
            'abonnement': service_pal[1],
            'restaurant': food_palette[1],
            'bar': food_palette[2],
            'food shopping': food_palette[3],
            'bank transfer': inc_money_pal[1],
            'event': shopping_pal[1],
            'service': service_pal[2],
            'speed food': food_palette[4],
            'health': service_pal[3],
            'school': service_pal[7],
            'extern transfer': inc_money_pal[2],
            'intern transfert': inc_money_pal[3],
            'rent': service_pal[6],
            'fee and loan': inc_money_pal[6],
            'interest': inc_money_pal[4],
            'shopping': shopping_pal[2],
            'clothes shopping': shopping_pal[3],
            'tech shopping': shopping_pal[4],
            'furniture': shopping_pal[5],
            'tax & continuous service': service_pal[5],
            'stock exchange': inc_money_pal[5],
            "travel" :service_pal[6],
            "Other" : 'rgb(0,0,0)'
        }
    
    
    data = pd.read_excel((path_source+r"\data_operations.xlsx").replace("\\","/"))
    
    data.set_index("Date",inplace=True)
    df_cc=data.loc[data["currency"]==currency]
    df_cc = df_cc.loc[df_cc["bank"].isin(banks)]
    df1 = df_cc.sort_index()
    df1.index = pd.to_datetime(df1.index)
    df2= df1.groupby([pd.Grouper(freq='M'), 'category'])['amount'].sum()
    df_tot = df1.groupby([pd.Grouper(freq='M')])['amount'].sum()
    df2=df2.reset_index()
    df2.set_index("Date",inplace=True)
    df2["differences"]=df_tot.round(2)
    df2=df2.reset_index()
    #df2["Date"] =  df2["Date"]-datetime.timedelta(days=28)
    
    df2.loc[df2["amount"]<0,"type"]="expenses"
    df2.loc[df2["amount"]>0,"type"]="incomes"
    
    
    
    #df2.loc[df2["amount"]<0,"Date"] =  df2.loc[df2["amount"]<0]["Date"]+datetime.timedelta(days=10)
    df2["amount"]=df2["amount"].abs()

    
    
    df2=df2.sort_values(by="Date",ascending=True).set_index("Date").last(f"{nb_month}M")
    df2=df2.reset_index()
    if normalized :
        df_sum = df2.groupby(["Date","type"])['amount'].sum()
        
        for d in df_sum.index:
            
            df2.loc[((df2["Date"]==d[0]) & (df2["type"]==d[1])),"amount"]=(df2.loc[((df2["Date"]==d[0]) & (df2["type"]==d[1])),"amount"]*10000/df_sum.loc[d]).astype("int")/100
    df2["Date_2"]=df2["Date"].copy()
    df2["Date"]=df2["Date"].dt.strftime('%b%y')
    df2= df2.sort_values("Date")
    layout = go.Layout(barmode='stack',autosize=False,width=1900,height=700)
    fig = go.Figure(layout=layout)
    
    #fig.update_layout(
    #template="simple_white",
    #xaxis=dict(title_text="Date"),
    #yaxis=dict(title_text="Amount in {currency}"),
    #barmode="stack")
    
    df_init = df2[["Date","differences","type","Date_2"]].drop_duplicates()
    df_init= df_init.sort_values(["Date_2","type"])
    df_init["amount"]=0
    
    
    fig.add_trace(go.Bar(x=[df_init["Date"]+" : "+df_init["differences"].astype("str"),df_init["type"]], y=df_init["amount"]))
    #                     category_orders=df_init["Date"]))
    #fig.add_trace(go.Bar(x=[df_init["Date"]+" : "+df_init["differences"].astype("str"),"incomes"], y=df_init["amount"]))
    
    for cat in df2.category.unique():
        #offsetgroup= 0+
        plot_df = df2[df2.category==cat]
        fig.add_trace(go.Bar(x=[plot_df["Date"]+" : "+plot_df["differences"].astype("str"),plot_df["type"]], y=plot_df["amount"], name=cat,marker_color=color_discrete_map[cat]))
    
    
    
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=f"Amount in {currency}")
    #fig.update_xaxes(categoryorder='category ascending')
    #fig.layout.xaxis.tickvals = pd.date_range(min(df2["Date_2"]), max(df2["Date_2"]), freq='MS')
    #fig.layout.xaxis.tickformat = '%b'
    
    return fig

if __name__ == "__main__":
    currency = "CHF"
    banks = ["CS"]
    fig = create_fig(currency,banks,normalized=False,nb_month=6)
    plot(fig)


