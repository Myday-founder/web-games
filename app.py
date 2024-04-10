from flask import Flask,render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///login_data.db"
db = SQLAlchemy(app)


class User(db.Model):
    username = db.Column(db.String(80), primary_key=True, nullable=False)

    def __repr__(self):
        return f'{self.username}'


    
with app.app_context():
    db.create_all()    


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/process_login', methods=['POST'])
def process_login():
    if request.method == 'POST':
        username = request.form['username']
        new_user = User(username=username)
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
        
def generate_bingo_board():
    # Generate a list of unique numbers from 1 to 25
    numbers = list(range(1, 26))
    # Shuffle the list of numbers
    random.shuffle(numbers)
    # Create the Bingo board by taking the first 25 numbers from the shuffled list
    board = numbers[:25]
    return board

@app.route('/bingo')
def bingo_game():
    users = User.query.all()
    current_user_index = len(users) % 3  # Calculate the index of the current user's turn
    current_user = users[current_user_index].username if users else None
    bingo_board = generate_bingo_board()
    return render_template('bingo_board.html', users=users, current_user=current_user, bingo_board=bingo_board)

@app.route('/process_turn', methods=['POST'])
def process_turn():
    if request.method == 'POST':
        chosen_number = int(request.form['number'])
        # Get the Bingo board from the form data
        bingo_board = [int(request.form[f'cell-{i}']) for i in range(25)]
        # Mark the chosen number on the Bingo board
        for i, number in enumerate(bingo_board):
            if number == chosen_number:
                bingo_board[i] = 'X'  # Mark the chosen number as 'X'
        return render_template('bingo_board.html', bingo_board=bingo_board)




if __name__ == '__main__':
    app.run(host='0.0.0.0')

