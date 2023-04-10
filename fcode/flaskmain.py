from flask import Flask,request,redirect,flash,render_template,url_for,send_file,make_response
from flask import session as flsession
from flask_login import login_user,login_required, logout_user, current_user
from io import StringIO
from forms import *
import models
from sqlalchemy import MetaData,Table
import requests
from crud import logger
import pandas as pd
from database import SessionLocal, engine
# from forms import *
# from models import *
from logger import *





session=SessionLocal()

@app.route('/', methods=['GET', 'POST'])
# @login_required
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        
        username=form.username.data
        password=form.password.data
        payload = {'username': username, 'password': password}
        res=requests.post('http://localhost:8000/token', data=payload)
        try:
            token = res.json()["access_token"]
            flsession['token']=token
            return render_template('profilepage.html',current_user=current_user,username=username)
        except Exception:
            flash("Enter Correct Username/password")
            return render_template('adminlogin.html',form=form)
        
        
    return render_template('adminlogin.html',form=form)


    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form=StudentForm()
    if form.validate_on_submit():
        username = request.form['username']    
        email=request.form['email'] 
        password=request.form['password']
        place=request.form['place']
        payload={'username':username,'email':email ,'password':password,'place':place}
        response=requests.post('http://localhost:8000/create/user/', json=payload)
        if response.status_code==201:
            logger.error("Entered Username exists")          
            flash("User is Registered")
        elif response.status_code==406:
          logger.error(response.json()['detail']) 
          flash(response.json()['detail'])
        elif response.status_code==400:
           logger.error(response.json()['detail']) 
           flash(response.json()['detail'])
        
        return render_template('accreg.html',form=form)
    else:
        return render_template('accreg.html',form=form)





@app.route('/upload', methods=['GET', 'POST'])
def uploadcsv():
    if request.method == 'POST':
        token = flsession['token']
        file = request.files['file']
        headers={'Authorization': "Bearer {}".format(token)}
        payload={'file': file.read()}
        response = requests.post("http://localhost:8000/uploadfile/",headers=headers,files=payload)
        dbid=response.json()['ID']
        print(dbid)
        return redirect(url_for('taskStatus',dbid=dbid))  
    else:
       
        return render_template('uploadfile.html')

@app.route('/task/status', methods=['GET', 'POST'])
def taskStatus():
        token = flsession['token']
        dbid=request.args.get('dbid')
        print(dbid)
        params={"idd":dbid}
        headers={'Authorization': "Bearer {}".format(token)}
        response2 = requests.get("http://localhost:8000/status/",params=params,headers=headers)
        status=response2.json()['Status']
        try:
            useritem = session.query(models.review1).filter(models.review1.id == dbid).first()
            session.close
        except Exception as e:
            session.rollback()
            print(e)
            logger.error("DB error:",e) 
            session.close()        
        if status == "success":
            dbtable = pd.read_json(useritem.data)
            dbdict = dbtable.to_dict('records')
            return render_template('alldetailstb.html', status=status,dbdict=dbdict,dbid=dbid)
        elif status == "progressing":
            return render_template('alldetailstb.html', status=status)
            
        elif    status == "failed":
            return render_template('alldetailstb.html', status=status)

                  

@app.route('/download')
def downloadFile ():
    dbid=request.args.get('dbid')
    try:
        useritem = session.query(models.review1).filter(models.review1.id == dbid).first()
        session.close
    except Exception as e:
        session.rollback()
        print(e)
        logger.error("DB error:",e)  
        session.close()
    dbtable = pd.read_json(useritem.data,orient='records')
    csvdata=dbtable.to_csv(index=False)
    csvdata=StringIO(csvdata)
    response=make_response(csvdata.getvalue())
    response.headers['Content-Disposition']='attachment; filename=Predicted Review.csv'
    response.headers['Content-Type']='text/csv'
    return response


@app.route('/adminlogout', methods=['GET', 'POST'])
@login_required
def adminlogout():
    logout_user()
    return redirect(url_for('signin'))


@app.route('/del', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        username = request.form['username']
        url = f"http://localhost:8000/delete"
        requests.delete(url,params={'username':username})
        return redirect(url_for('signin'))
    else:
        return render_template('profilepage.html')

@app.route('/change', methods=['GET', 'POST','PUT'])
def changepass():
    form=passwordForm()
    if form.validate_on_submit():
        username = request.form['username']
        password=request.form['password']
        newpassword=request.form['newpassword']
        payload={'username':username,'password':password,'newpassword':newpassword}
        requests.put('http://localhost:8000/changepass',params=payload)
        return render_template('profilepage.html')
    else:
        return render_template('changepass.html',form=form)


if __name__ == "__main__":
   app.run()



