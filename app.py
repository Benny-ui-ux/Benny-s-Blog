import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
from dotenv import load_dotenv
import sqlite3
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SESSION_COOKIE_PATH'] = '/'


# Set predefined username and password from environment variables
USERNAME = os.getenv('FLASK_LOGIN_USER')
PASSWORD = os.getenv('FLASK_LOGIN_PASSWORD')

# Set up database
DATABASE = 'blog.db'

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Close the database connection when the app context is torn down
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize the database (if not already created)
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS posts (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          title TEXT NOT NULL,
                          content TEXT NOT NULL
                      );''')
        db.commit()

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session.permanent = True
            session['logged_in'] = True
            print("Logged in status:", session.get('logged_in'))
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')
# Route for editing a post
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Get updated post title and content
        new_title = request.form['title']
        new_content = request.form['content']
        
        # Update the post in the database
        cursor.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', 
                       (new_title, new_content, post_id))
        db.commit()
        flash('Post updated successfully.')
        return redirect(url_for('index'))
    
    # Fetch the existing post to display in the form
    cursor.execute('SELECT title, content FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    
    if post:
        return render_template('edit_post.html', post_id=post_id, title=post[0], content=post[1])
    else:
        return "<p>Post not found.</p>", 404

# Route for deleting a post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()
    flash('Post deleted successfully.')
    return redirect(url_for('index'))


# Route for logging out
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

# Home and other static routes
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

# Route for displaying the post submission form
@app.route('/submit_post')
def submit_post_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('submit_post_form.html')

# Route to handle post submission
@app.route('/submit_post', methods=['POST'])
def submit_post():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    title = request.form['title']
    content = request.form['content']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
    db.commit()
    
    flash('Post successfully added!')
    return redirect(url_for('index'))

# Function to retrieve all posts from the database
def get_all_posts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title, content FROM posts ORDER BY id DESC')
    posts = cursor.fetchall()
    return [{'id': post[0], 'title': post[1], 'content': post[2]} for post in posts]

# Route to display all posts
@app.route('/get_posts', methods=['GET'])
def get_posts():
    posts = get_all_posts()
    return render_template('posts.html', posts=posts)

# Route to display the content of a single post
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

# Main entry point for the app
if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)

