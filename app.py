from flask import Flask, render_template, redirect, request, url_for, session, flash
from functools import wraps
import pymongo
from bson import ObjectId

app = Flask(__name__)
app.secret_key = '#&Q@E@23JGH@J29DKJBSBIHVFIYy082y89tegwhvd'
LOGGED_IN = 'logged_in'



dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
print(dbclient.list_database_names())
db = dbclient["notes"]
notes = db['notes']
auth = db['auth']





fake_data = [{
    "name": "Waseem",
    "id": "abcd"
}, {
    "name": "Hello",
    "id": "efgh"
}, {
    "name": "World",
    "id": "ijkl"
}, {
    "name": "Blah Blah",
    "id": "mnop"
}]


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if LOGGED_IN in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if username == '' or password == '':
            error = "Invalid username or password, Please try again"
        else:
            auth.insert_one({'username':username,'password':password})
            return redirect(url_for('login'))
    return render_template("register.html", error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        data = auth.find_one({'username':username})
        if password != data['password']:
            error = "Invalid Credentials! Please try again"
        else:
            session[LOGGED_IN] = True
            return redirect(url_for('home'))
    return render_template("login.html", error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop(LOGGED_IN, None)
    return redirect(url_for('home'))


@app.route('/')
@login_required
def home():
    return render_template('index.html', result=[x for x in notes.find()])


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    error = None
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if title.strip() == "":
            error = "Please Enter the title"
        elif content.strip() == "":
            error = "Please Enter the content"
        else:
            notes.insert_one({
                "title": title,
                "content": content
            })
            return redirect(url_for('home'))

    return render_template('addNote.html', addNote="active", error=error)



@app.route('/show/<id>')
@login_required
def show(id):
    data = notes.find_one({'_id':ObjectId(id)})
    return render_template('noteView.html',title=data['title'],content=data['content'],id=data['_id'])


@app.route('/remove/<id>')
@login_required
def remove(id):
    notes.delete_one({'_id':ObjectId(id)})
    return redirect(url_for('home'))






if __name__ == '__main__':
    app.run(debug=True, port=4000)
