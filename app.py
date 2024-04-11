from flask import Flask,render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy



import random



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://login_data_user:l3qUPNplfII866iBalPXsuvHI3Hc3Ves@dpg-cobqe8gcmk4c73adnv40-a.singapore-postgres.render.com/login_data"

db = SQLAlchemy(app)


class User(db.Model):
    username = db.Column(db.String(80), primary_key=True, nullable=False)

    def __repr__(self):
        return f'{self.username}'

class BingoBoard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), db.ForeignKey('user.username'))
    board = db.Column(db.PickleType)

    def __repr__(self):
        return f'{self.user_id}'

    
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
        
        # Check if the user already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return redirect(url_for('index'))
        
        # If the user does not exist, add a new user
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('index'))

        
def generate_bingo_board(existing_board=None, chosen_numbers=None):
    if existing_board:
        return existing_board
    
    numbers = list(range(1, 26))
    random.shuffle(numbers)
    
    if chosen_numbers:
        board = ['#' if number in chosen_numbers else number for number in numbers[:25]]
    else:
        board = numbers[:25]
    
    return board




@app.route('/bingo')
def bingo_game():
    users = User.query.all()
    total_users = len(users)
    current_user_index = request.args.get('user_index', default=0, type=int)
    current_user = users[current_user_index].username if users else None
    bingo_board_data = BingoBoard.query.filter_by(user_id=User.query.all()[current_user_index].username).first()
    bingo_board = bingo_board_data.board if bingo_board_data else generate_bingo_board()
    return render_template('bingo_board.html', users=users, total_users=total_users, current_user=current_user, current_user_index=current_user_index, bingo_board=bingo_board)




@app.route('/process_turn', methods=['POST'])
def process_turn():
    if request.method == 'POST':
        chosen_number = int(request.form['number'])
        current_user_index = int(request.form['user_index'])
        
        # Get the current user
        users = User.query.all()
        current_user = users[current_user_index]
        
        # Get the bingo board data for the current user
        bingo_board_data = BingoBoard.query.filter_by(user_id=current_user.username).first()
        
        # If there's no bingo board data for the current user, create a new one
        if not bingo_board_data:
            bingo_board = generate_bingo_board(chosen_numbers=[chosen_number])  # Pass chosen_number here
            bingo_board_data = BingoBoard(user_id=current_user.username, board=bingo_board)
            db.session.add(bingo_board_data)
        else:
            bingo_board = bingo_board_data.board
        
        # Mark the chosen number on the Bingo board with '#'
        for i, number in enumerate(bingo_board):
            if number == chosen_number:
                bingo_board[i] = '#'  # Mark the chosen number as '#'
        
        # Update the Bingo board in the database for all users
        for user in users:
            user_bingo_board_data = BingoBoard.query.filter_by(user_id=user.username).first()
            if user_bingo_board_data:
                user_bingo_board_data.board = generate_bingo_board(existing_board=bingo_board, chosen_numbers=[chosen_number])  # Pass existing board and chosen_number here
        db.session.commit()
        
        # Calculate the index of the next user
        next_user_index = (current_user_index + 1) % len(users)
        
        # Redirect to the bingo board page with the next user index
        return redirect(url_for('bingo_game', user_index=next_user_index))


@app.route('/clear')
def close():
    db.session.query(BingoBoard).delete()
    db.session.query(User).delete()
    db.session.commit()
    return "Database cleaned up successfully!"



if __name__ == '__main__':
    app.run()

