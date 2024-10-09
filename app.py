from flask import Flask, render_template, request, jsonify, g, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = 'Enter_Database_Location'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS posts (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          title TEXT NOT NULL,
                          content TEXT NOT NULL
                      );''')
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/submit_post')
def submit_post_page():
    return render_template('submit_post_form.html')

@app.route('/submit_post', methods=['POST'])
def submit_post():
    title = request.form['title']
    content = request.form['content']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
    db.commit()
    
    # Return a success message instead of redirecting
    return "<p>Post successfully added!</p>"

def get_all_posts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title, content FROM posts ORDER BY id DESC')
    posts = cursor.fetchall()
    return [{'id': post[0], 'title': post[1], 'content': post[2]} for post in posts]

@app.route('/get_posts', methods=['GET'])
def get_posts():
    posts = get_all_posts()
    return render_template('posts.html', posts=posts)

@app.route('/post_content/<int:post_id>', methods=['GET'])
def post_content(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT content FROM posts WHERE id = ?', (post_id,))
    post_content = cursor.fetchone()
    
    if post_content:
        return f"<p>{post_content[0]}</p>"
    else:
        return "<p>Post content not found.</p>", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

