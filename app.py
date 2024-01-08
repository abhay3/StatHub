from flask import Flask,  render_template, url_for, request,session, redirect
from flask_mysqldb import MySQL
import re
import os

app=Flask(__name__)

app.secret_key = os.urandom(24)

app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Aadi200#"
app.config["MYSQL_DB"] = "basketball"
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template('login.html')

@app.route("/home.html")
def home():
    return render_template('home.html')

@app.route("/schedule.html")
def schedule():
    return render_template('schedule.html')

@app.route("/teams.html")
def teams():
    cur=mysql.connection.cursor()
    values = cur.execute("SELECT * FROM TEAMS")
    if values > 0:
        details = cur.fetchall()
        return render_template('teams.html',details=details)

@app.route('/players.html')
def players():
    cur=mysql.connection.cursor()
    #NESTED QUERY
    values = cur.execute("SELECT Name AS Player, Pos, Age, ( SELECT TeamName FROM Teams WHERE Teams.TeamID = Players.TeamID) AS TeamName FROM Players")
    if values > 0:
        details = cur.fetchall()
        return render_template('players.html',details=details)
    
@app.route("/team_standings.html")
def team_standings():
    cur=mysql.connection.cursor()
    #FUNCTION + AGGREGATE QUERY + JOIN QUERY
    values = cur.execute("CALL team_standings()")
    if values > 0:
        details = cur.fetchall()
        return render_template('team_standings.html',details=details)

@app.route("/coaches.html")
def coaches():
    cur=mysql.connection.cursor()
    #JOIN QUERY 
    values = cur.execute("SELECT Coaches.Name AS CoachName, Teams.TeamName FROM Coaches JOIN Teams ON Coaches.TeamID = Teams.TeamID")
    if values > 0:
        details = cur.fetchall()
        return render_template('coaches.html',details=details)

@app.route('/login.html', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            if user[2]==email and user[3]==password:
                msg = 'Logged in successfully!'
                return render_template('user.html', msg = msg)
            else:
                msg = 'Please enter correct email / password !'
        else:
            msg = 'Please enter correct email / password !'
    return render_template('login.html', msg = msg)

@app.route('/user.html')
def user():
    return render_template('user.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register.html', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            # AGGREGATE QUERY 
            cursor.execute('select count(userid) from user')
            number = cursor.fetchone()
            number = number[0] + 1
            cursor.execute('INSERT INTO user VALUES (% s, % s, % s, % s)', (number, userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered! Go to login page'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)

@app.route("/player_stats.html")
def stats():
    cur=mysql.connection.cursor()
    values = cur.execute("CALL GetTopPlayerStats()")
    if values > 0:
        details = cur.fetchall()
        return render_template('player_stats.html',details=details)

@app.route("/allstats.html")
def all_stats():
    cur=mysql.connection.cursor()
    values = cur.execute("CALL GetPlayerStats()")
    if values > 0:
        details = cur.fetchall()
        return render_template('allstats.html',details=details)
    
@app.route("/adv.html")
def adv():
    cur=mysql.connection.cursor()
    values = cur.execute("CALL GetTeamStatsWithTeamName()")
    if values > 0:
        details = cur.fetchall()
        return render_template('adv.html',details=details)

if __name__ == "__main__":
    app.run(debug=True)


