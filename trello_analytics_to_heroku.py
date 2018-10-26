from pprint import pprint
import requests
import json
import pandas as pd
from slackclient import SlackClient
import os
import datetime


def get_data_from_API():
    url = "https://api.trello.com/1/boards/5bc90376dd9b1466d5255e22"
    querystring = {"actions":"none","boardStars":"none","cards":"visible","card_pluginData":"false","checklists":"all","customFields":"true","fields":"name,desc,descData,closed,idOrganization,pinned,url,shortUrl,prefs,labelNames","lists":"open","members":"none","memberships":"none","membersInvited":"none","membersInvited_fields":"all","pluginData":"false","organization":"false","organization_pluginData":"false","myPrefs":"false","tags":"false","key":"aa58caeba1675b65b46ba15f8dc9282d","token":"5d169c96fafd3b832efbccb692febc7c8971a24231d97414addc7e5b97e649a3"}
    response = requests.request("GET", url, params=querystring)
    data = json.loads(response.text)
    return data

def get_tickets(data):
    columns = {"ticket_id","ticket_title","points","priority","labels","owner","list_id"}
    df = pd.DataFrame(columns=columns)
    i = 0
    count = 0
    while i < len(data['cards']):
        if data['cards'][i]['closed'] == False and data['cards'][i]['idList'] <> "5bc903931f4d7274c740d1ef":
            count += 1
            index = len(df)
            df.loc[index,'ticket_id'] = data['cards'][i]['id']
            df.loc[index,'ticket_title'] = data['cards'][i]['name']
            #df.loc[len(df),'points'] = 
            #df.loc[len(df),'priority']
            df.loc[index,'labels'] = data['cards'][i]['labels']
            df.loc[index,'owner'] = data['cards'][i]['idMembers']
            df.loc[index,'list_id'] = data['cards'][i]['idList']
        i += 1
    return(df)
    
def get_list_label(data) :
    df = pd.DataFrame(columns={'list_id','list_name'})
    list_names = data['lists']
    i = 0
    while i < len(data['lists']):
        index = len(df)
        df.loc[index,'list_id'] = data['lists'][i]['id']
        df.loc[index,'list_name'] = data['lists'][i]['name']
        i += 1
    return(df)
    df.to_csv("lists_names.csv",sep=";",encoding='utf-8')

def label_list(df1,df2,mixed_columns):
    df3 = pd.merge(df1, df2, on=mixed_columns)
    df3.to_csv('ticket_info.csv', sep=';',encoding='utf-8')
    return(df3)


def get_team_from_label(data):
    team_list = ['Front','API','DPS','PI','OPS','Math','QA','Support','Archi.']
    i = 0
    while i < len(data):
        nb_of_labels = len(data.loc[i,'labels'])
        j = 0
        while j < nb_of_labels :
            for k in team_list :
                if data.loc[i,'labels'][j]['name'] == k :
                    data.loc[i,str('team')] = k
            j += 1
        i += 1
    return(data)    

def get_data() :
    data1 = get_data_from_API()
    data = get_tickets(data1)
    list_names = get_list_label(data1)
    data = label_list(data,list_names,"list_id")
    data = get_team_from_label(data)
    data.to_csv('ticket_info.csv', sep=';',encoding='utf-8')

def get_stats_per_team(data_file):
    data = pd.read_csv(data_file,sep=";")
    data = data.groupby(['team','list_name'])['ticket_id'].count()
    print(data)

def get_stats_per_list(data_file):
    data = pd.read_csv(data_file,sep=";")
    data = data.groupby(['list_name'])['ticket_id'].count()
    return(data)

def send_slack_message(msg) :
    
    url = "https://slack.com/api/chat.postMessage?token=xoxp-2503013600-150008235968-465254622579-5736ddbc9bd2f156deaa382479376b4b&channel=test-adrien-vincent&text="+msg+"&username=Scrum%20Bot&icon_url=https%3A%2F%2Fcdn4.iconfinder.com%2Fdata%2Ficons%2Fthefreeforty%2F30%2Fthefreeforty_target-512.png&pretty=1"
    
    r = requests.post(url)
    print(r)

def create_message(data):
    now = datetime.datetime.now()
    msg = "["+str(now.strftime("%Y-%m-%d %H:%M"))+"]"+"\n:rocket: *Sprint Update - Trello Card Status* :rocket:"+"\n*Total of Cards* : "+ str(data.sum()) + "\n *To Do* : " + str(data["To Do"]) + "\n *In Progress* : " + str(data["In Progress"]) + "\n *Done* : " + str(data["Done"])
    return(msg)
    


get_data()
data = get_stats_per_list('ticket_info.csv')
msg = create_message(data)
send_slack_message(msg)