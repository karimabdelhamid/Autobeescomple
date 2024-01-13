from flask import Flask, render_template, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key

# Store game data
game_data = {
    'letters_used': [],
    'current_letter': '',
    'players': {},
    'scores': {}
}

# Categories for the game
CATEGORIES = ['Boy Name', 'Girl Name', 'Inanimate', 'Animal', 'Food', 'Country', 'Celebrity']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['GET', 'POST'])
def start_game():
    if request.method == 'POST':
        session['player_name'] = request.form['player_name']
        game_data['players'][session['player_name']] = {'is_ready': False, 'answers': {}}
        game_data['scores'][session['player_name']] = 0
        return redirect(url_for('enter_answers'))
    return render_template('start.html')

@app.route('/answers', methods=['GET', 'POST'])
def enter_answers():
    if 'player_name' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        answers = {category: request.form[category] for category in CATEGORIES}
        game_data['players'][session['player_name']]['answers'] = answers
        game_data['players'][session['player_name']]['is_ready'] = True
        if all(player['is_ready'] for player in game_data['players'].values()):
            return redirect(url_for('score_round'))
        return render_template('waiting.html')
    else:
        game_data['current_letter'] = generate_random_letter()
        return render_template('answers.html', letter=game_data['current_letter'], categories=CATEGORIES)

@app.route('/score')
def score_round():
    # This function will compare the answers and calculate scores
    compare_answers_and_calculate_scores()
    return render_template('scores.html', scores=game_data['scores'], players=game_data['players'])

def generate_random_letter():
    alphabet = string.ascii_uppercase
    available_letters = [letter for letter in alphabet if letter not in game_data['letters_used']]
    if not available_letters:
        return None
    letter = random.choice(available_letters)
    game_data['letters_used'].append(letter)
    return letter

# ...

def compare_answers_and_calculate_scores():
    for category in CATEGORIES:
        answers_in_category = [game_data['players'][player]['answers'][category] for player in game_data['players']]
        unique_answers = set(answers_in_category)
        for answer in unique_answers:
            if answer and answer[0].lower() == game_data['current_letter'].lower():
                score = 10 if answers_in_category.count(answer) == 1 else 5
                for player, player_data in game_data['players'].items():
                    if player_data['answers'][category].lower() == answer:
                        game_data['scores'][player] += score

    # Reset for the next round
    for player_data in game_data['players'].values():
        player_data['answers'].clear()
        player_data['is_ready'] = False

@app.route('/next_round', methods=['GET', 'POST'])
def next_round():
    if request.method == 'POST':
        game_data['current_letter'] = generate_random_letter()
        if game_data['current_letter'] is None:
            return redirect(url_for('game_over'))
        for player_data in game_data['players'].values():
            player_data['is_ready'] = False
        return redirect(url_for('enter_answers'))
    return render_template('next_round.html')

@app.route('/game_over')
def game_over():
    return render_template('game_over.html', scores=game_data['scores'])

@app.route('/reset_game', methods=['POST'])
def reset_game():
    game_data['letters_used'].clear()
    game_data['current_letter'] = ''
    game_data['players'].clear()
    game_data['scores'].clear()
    session.pop('player_name', None)
    return redirect(url_for('index'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

                


