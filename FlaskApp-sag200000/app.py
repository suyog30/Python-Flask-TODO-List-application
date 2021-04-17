from flask import Flask, render_template, request, json, redirect, jsonify
from flaskext.mysql import MySQL
from flask import session
import psycopg2
import collections

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'TodoList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)



app.secret_key = 'secret key can be anything!'


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        con = mysql.connect()
        cursor = con.cursor()
        

        cursor.execute("SELECT * FROM tbl_user WHERE email = %s", (_email))

        data = cursor.fetchall()


        if len(data) > 0:
            if str(data[0][3]) == _password:
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')


    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()
 
@app.route('/signUp',methods=['POST'])
def signUp():
 
    # read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
 
    # validate the received values
    if _name and _email and _password:

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO tbl_user(name, email, password) VALUES (%s, %s, %s)", (_name, _email, _password))
        

        data = cursor.fetchall()

        if len(data) == 0:
            conn.commit()
            return json.dumps({'message':'User created successfully !'})
        else:
            return json.dumps({'error':str(data[0])})


    else:
        return json.dumps({'html':'<span>Enter the required fields!</span>'})

@app.route('/showAddItem')
def showAddItem():
    return render_template('addItem.html')

@app.route('/addItem',methods=['POST'])
def addItem():
    try:
        if session.get('user'):
            _title=request.form['inputTitle']
            _description=request.form['inputDescription']
            _user=session.get('user')

            conn=mysql.connect()
            cursor=conn.cursor()

            cursor.execute("INSERT INTO tbl_todo(title,description,userid) VALUES (%s,%s,%s)", (_title,_description,_user))

            data=cursor.fetchall()
            if len(data)==0 :
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error='An error occured!')

        else:
            return render_template('error.html',error='Unauthorized access')

    except Exception as e:
        return render_template('error.html', error=str(e))        

@app.route('/ListFetch',methods=['GET'])
def ListFetch():
    try:
        if session.get('user'):
            _user=session.get('user')

            conn=mysql.connect()
            cursor=conn.cursor()

            cursor.execute("Select id,title,description,IsComplete from tbl_todo where userid= %s", (_user))

            data=cursor.fetchall()
            objects_list = []
            for row in data:
                d = collections.OrderedDict()
                d["id"] = row[0]
                d["title"] = row[1]
                d["description"] = row[2]
                d["IsComplete"] = row[3]
                objects_list.append(d)

            return json.dumps(objects_list)

        else:
            return render_template('error.html',error='Unauthorized access')

    except Exception as e:
        return render_template('error.html', error=str(e))     
    
@app.route('/showEditItem')
def showEditItem():
    if session.get('user'):
        number= request.args.get('number', None)
        return render_template('editItem.html',number=number)
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/editFetch',methods=['GET'])
def editFetch():
    try:
        if session.get('user'):
            _user=session.get('user')
            number= request.args.get('number', None)
            

            conn=mysql.connect()
            cursor=conn.cursor()

            cursor.execute("Select id,title,description,IsComplete from tbl_todo where id= %s", (number))

            data=cursor.fetchall()
            objects_list = []
            for row in data:
                d = collections.OrderedDict()
                d["id"] = row[0]
                d["title"] = row[1]
                d["description"] = row[2]
                d["IsComplete"] =row[3]
                objects_list.append(d)

            return json.dumps(objects_list)

        else:
            return render_template('error.html',error='Unauthorized access')

    except Exception as e:
        return render_template('error.html', error=str(e))     

@app.route('/editItemSubmit',methods=['POST'])
def editItemSubmit():
    try:
        if session.get('user'):
            _title=request.form['inputTitle']
            _description=request.form['inputDescription']
            _user=session.get('user')
            _IsComplete=request.form.get('IsCompleted')
            number= request.args.get('number', None)
            if _IsComplete == 'on':
                _IsComplete = 1
            else:
                _IsComplete = 0

            conn=mysql.connect()
            cursor=conn.cursor()

            cursor.execute("Update tbl_todo Set title=%s,description=%s,IsComplete=%s where id=%s", (_title,_description,_IsComplete,number))

            data=cursor.fetchall()
            if len(data)==0 :
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error='An error occured!')

        else:
            return render_template('error.html',error='Unauthorized access')

    except Exception as e:
        return render_template('error.html', error=str(e))        

@app.route('/deleteItems',methods=['GET','POST','DELETE'])
def deleteItem():
    try:
        if session.get('user'):
            _user=session.get('user')
            number= request.args.get('number', None)

            conn=mysql.connect()
            cursor=conn.cursor()

            cursor.execute("Delete from tbl_todo where id=%s", (number))

            data=cursor.fetchall()
            if len(data)==0 :
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error='An error occured!')

        else:
            return render_template('error.html',error='Unauthorized access')

    except Exception as e:
        return render_template('error.html', error=str(e))    

if __name__ == "__main__":
    app.run()   




