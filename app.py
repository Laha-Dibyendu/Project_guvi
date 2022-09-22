from ast import Global
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
from bs4 import BeautifulSoup
import requests
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from flask_security import login_required, logout_user

app = Flask(__name__)

@app.route('/',methods=["GET"])
def index():
    return render_template('index.html')



@app.route('/show', methods=['POST', 'GET'])
def show_me():
    email=request.form.get('email')
    
    password=request.form.get('pasw')
    #Global query_category query_subcategory, query_status, user_status, program_name

    #Variables for using
    my_column_names = ['Query_Id','Category','Sub-Category','Language','learner_name','learner_email',"learner_status","learner_batch_name","learner_batch_type","Program",
                   'Query_Created_At',
                   'Assigned_to','Assigned_Time','Last_Status','resolved_time',"closed_time","is_transferred?",
                   'Mentor_Rating_point']
    query_category = {1:"Zen Class Doubt",2:"Placement Related",3:"Coordination Related",4:"Pre-Bootcamp"}

    query_subcategory = {101:"Task",102:"Hackathon",103:"Class Topic",104:"Webkata",105:"Codekata",106:"Assessment",
                        201:"Company Info",202:"Completion Certificate",203:"Portfolio",
                        301:"Session Timing",302:"Session Joining Link",303:"Session Feedback",304:"Completion Certificate",305:"Payment",
                        401:"Session",402:"Payment",403:"CodeKata",404:"WebKata",405:"Task",406:"Other" }

    query_status = {1:"Active",2:"Assigned",3:"Resolved",4:"Closed",5:"Transferred"}

    user_status={ 1:"Active Lead",2:"Preboot Camp",3:"Mainboot Camp ",4:"Placement Preparing",5:"Placement Ready",
                6:"Shortlisted", 7:"Placed", 8:"Disabled", 9:"On Hold", 10:"Placement Waiting"
                }

    program_name={
        1:"FSD-MERN",2:"FSD-MEAN",3:"MASTER DATA SCIENCE",4:"AUTOMATION TESTING",5:"FSD-MERP",6:"FSD-MERJ",7:"Cyber Security",
        8:"Front-end Development React",9:"Front-end Development Angular",10:"Advanced Python Course",11:'Business Analytics',
        12:"Master Data Engineering",13:"UI/UX Design",14:"Core Java Programming",15:"Devops",16:"Appreneur",17:"Automation Testing Java",
        18:"Master BA & DM",19:"IITM-ML Engineer",20:"AutoCAD Mech"
        }

    # Accesing the api with Auth key
    response33 = requests.post('https://api.zenclass.in/api/v1/login',
            data={"email":email, "password":password})

    headers = {
    'Authorization': 'Bearer '+response33.json()["token"]}
    params = {
        'page': 1,
        'limit': 10,
        'fromDate': '2022-09-13',
        'toDate': '2022-09-15'
    }
    response = requests.get('https://api.zenclass.in/api/v1/ticket/get-tickets?',
                            headers=headers, params=params)
    data=response.json()
    
    #Creating Data Frame
    main_mine = []

    for i in range(len(data["records"])):
        frame=[]
        frame.append(data["records"][i]['queryNumber'])                               #Query Number
        frame.append(query_category[data["records"][i]["category"]])                  ## Appending Category
    
        if data["records"][i]["subcategory"]:
            frame.append(query_subcategory[data["records"][i]["subcategory"]])          #Appending SubCategory
        else:
            frame.append("")

        frame.append(data["records"][i]["language"])    # Language

        user_hash={"hash":data["records"][i]["created"]["by"]}                        #User Details
        user = requests.post('https://api.zenclass.in/api/v1/users/get-user',
                                headers=headers, data=user_hash)
        user_details=user.json()

        frame.append(user_details["user"]["name"])
        frame.append(user_details["user"]["email"])
        frame.append(user_status[user_details["user"]["status"]])
        
        #batch = requests.get("https://api.zenclass.in/api/v1/batch/byId/"+user_details["user"]["batch"]+"?",headers=headers)
        if "batch" in user_details["user"].keys():
            batch = requests.get("https://api.zenclass.in/api/v1/batch/byId/"+user_details["user"]["batch"]+"?",headers=headers)
            batch_details=batch.json()
            frame.append(batch_details["batch"]["name"])
            frame.append(batch_details["batch"]["type"])
            
            if "program" in batch_details["batch"].keys():
                frame.append(program_name[batch_details["batch"]["program"]])
            else:
                frame.append("")
        else:
            frame.append("")
            frame.append("")
            frame.append("")
        #print(data["records"][i]["created"]['at'])    
        frame.append(datetime.strptime(data["records"][i]["created"]['at'][:-5], '%Y-%m-%dT%H:%M:%S'))
        #frame.append(data["records"][i]["created"]['at'])                             # Query cretion time
        
        if "to" in data["records"][i]['assigned'].keys():
            mentor_hash={"hash":data["records"][i]['assigned']["to"]}                     #mentor details
            mentor = requests.post('https://api.zenclass.in/api/v1/users/get-user',
                                    headers=headers, data=mentor_hash)
            mentor_details=mentor.json()
            frame.append(mentor_details["user"]["name"])                                  # assigned to
            #frame.append(data["records"][i]["assigned"]['at'])                            # Assigned time
            frame.append(datetime.strptime(data["records"][i]["assigned"]['at'][:-5], '%Y-%m-%dT%H:%M:%S'))
        else:
            frame.append("")
            frame.append("")
        if len(data["records"][i]['updated'])!=0:
            frame.append(query_status[data["records"][i]['updated'][-1]['action']])       #Last Update status
            
            r=False
            for j in range(len(data["records"][i]['updated'])):
                if data["records"][i]['updated'][j]['action']==3:
                    #frame.append(data["records"][i]['updated'][j]["at"])          #Resolved Time
                    frame.append(datetime.strptime(data["records"][i]['updated'][j]["at"][:-5], '%Y-%m-%dT%H:%M:%S'))
                    r=True
                    break
            if r ==False:
                frame.append("")

            c=False
            for j in range(len(data["records"][i]['updated'])):
                if data["records"][i]['updated'][j]['action']==4:
                    #frame.append(data["records"][i]['updated'][j]["at"])          #Closed Time
                    frame.append(datetime.strptime(data["records"][i]['updated'][j]["at"][:-5], '%Y-%m-%dT%H:%M:%S'))
                    c=True
                    break
            if c ==False:
                frame.append("")
            
            t=False
            for j in range(len(data["records"][i]['updated'])):  
                if data["records"][i]['updated'][j]['action']==5:
                    frame.append("Yes")
                    t=True
                    break                                           #Transferred ?
            if t ==False:
                frame.append("No")
        else:
            frame.append("")
            frame.append("")
            frame.append("")
            frame.append("No")

        if "rating" in data["records"][i].keys():  
            frame.append(data["records"][i]["rating"]['points'])
        else:
            frame.append("")

        main_mine.append(frame) # appending in bigger list

    my_data_prime = np.array(main_mine) # creating numpy array

    my_dataframe_ultimate = pd.DataFrame(data=my_data_prime, columns=my_column_names)
    
    # Creating another column in data frame to see the query resolving time
    Required_time=[]
    for i in range(my_dataframe_ultimate.shape[0]):
        if my_dataframe_ultimate["Assigned_Time"][i]:
            #Assigned_time = datetime.strptime(my_dataframe_ultimate["Assigned_Time"][i][:-5], '%Y-%m-%dT%H:%M:%S')
            Assigned_time = my_dataframe_ultimate["Assigned_Time"][i]
        else:
            Assigned_time=0
        if my_dataframe_ultimate["resolved_time"][i]: 
            #resolved_time = datetime.strptime(my_dataframe_ultimate["resolved_time"][i][:-5], '%Y-%m-%dT%H:%M:%S')
            resolved_time =my_dataframe_ultimate["resolved_time"][i]
        else:
            resolved_time=0
        if Assigned_time!=0 and resolved_time!=0: 
            time_required = resolved_time-Assigned_time
            Required_time.append(time_required)
        else:
            Required_time.append("Not Resolved yet")

    my_dataframe_ultimate["Required_time"]=Required_time
    #my_dataframe_ultimate.to_html("templates/show1.html",classes='table table-stripped')

    #Guvi_queries = pd.ExcelWriter('Guvi_queries.xlsx')
  
    # write DataFrame to excel
    my_dataframe_ultimate.to_csv("Guvi_queries.csv")
    
    # save the excel
    #Guvi_queries.save()
    

    return render_template("display.html",data={"d":my_dataframe_ultimate.to_html(classes='table table-hover')})
    #HTML(my_dataframe_ultimate.to_html(classes='table table-stripped'))
    #return render_template("display.html")


@app.route('/summary', methods=['POST', 'GET'])
def summary():
    fig, ax = plt.subplots(figsize=(7,5))
    my_dataframe_ultimate=pd.read_csv("Guvi_queries.csv")
    print(type(my_dataframe_ultimate))
    bars = ax.bar(my_dataframe_ultimate["learner_status"].unique(),my_dataframe_ultimate["learner_status"].value_counts())#.plot(kind='bar')
    for bar in bars:
        height = bar.get_height()
        label_x_pos = bar.get_x() + bar.get_width() / 2
        ax.text(label_x_pos, height, s=f'{height}', ha='center',
        va='bottom')

    plt.title('Count of queries from Leanrners')
    plt.xlabel('Learner Status')
    plt.ylabel('Count')


    #my_dataframe_ultimate["learner_status"].value_counts().plot(kind='bar')
    #plt.show()
    plt.savefig('static/plot.png', dpi = 100)
    #plt.savefig("first.png")

    fig = plt.figure(figsize =(8,5))
    plt.pie(my_dataframe_ultimate["learner_status"].value_counts(), labels =my_dataframe_ultimate["learner_status"].unique(),autopct='%1.2f%%' )
    plt.legend(loc ="center right",
            bbox_to_anchor =(-0.5, 0, 0.5, 1))
    plt.savefig('static/plot2.png', dpi = 100)

    fig, ax = plt.subplots(figsize=(7,5))
    bars2 = ax.bar(my_dataframe_ultimate["Sub-Category"].unique(),my_dataframe_ultimate["Sub-Category"].value_counts())#.plot(kind='bar')
    for bar in bars2:
        height = bar.get_height()
        label_x_pos = bar.get_x() + bar.get_width() / 2
        ax.text(label_x_pos, height, s=f'{height}', ha='center',
        va='bottom')
    
    plt.title('Count of Learners Sub-Category')
    plt.xlabel('Sub Category')
    plt.ylabel('Count')
    plt.savefig('static/plot3.png', dpi = 100)

    return render_template("summary.html")

@app.route('/download')
def download_file():
	path = "Guvi_queries.xlsx"
	return send_file(path, as_attachment=True)


@app.route('/show2', methods=['POST', 'GET'])
def show_me2():
    my_dataframe_ultimate=pd.read_csv("Guvi_queries.csv",index_col=0)
    return render_template("display.html",data={"d":my_dataframe_ultimate.to_html(classes='table table-hover')})


@app.route('/logout')
#@login_required
def logout():
    #logout_user()
    return redirect('/')

if __name__=='__main__':
    app.run(host='0.0.0.0',port='8080',debug=True)