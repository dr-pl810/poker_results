from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# Route to display the form and existing results
@app.route('/')
def index():
    conn = sqlite3.connect('poker.db')
    cursor = conn.cursor()

    # Fetch all players for the dropdown
    cursor.execute('SELECT * FROM players')
    players = cursor.fetchall()

    # Fetch all results with points
    cursor.execute('''
    SELECT results.date, 
           winner.name AS winner_name, 
           runner_up.name AS runner_up_name, 
           winner_points.points AS winner_points, 
           runner_up_points.points AS runner_up_points
    FROM results
    JOIN players AS winner ON results.winner_id = winner.id
    JOIN players AS runner_up ON results.runner_up_id = runner_up.id
    JOIN position_points AS winner_points ON results.winner_position = winner_points.position
    JOIN position_points AS runner_up_points ON results.runner_up_position = runner_up_points.position
    ORDER BY results.date DESC
    ''')
    results = cursor.fetchall()

    conn.close()
    return render_template('index.html', players=players, results=results)


# Route to handle form submission for adding results
@app.route('/add', methods=['POST'])
def add_result():
    date = request.form['date']
    winner_id = request.form['winner']
    runner_up_id = request.form['runner_up']

    conn = sqlite3.connect('poker.db')
    cursor = conn.cursor()

    # Insert the game result
    cursor.execute('''
    INSERT INTO results (date, winner_id, winner_position, runner_up_id, runner_up_position)
    VALUES (?, ?, 1, ?, 2)
    ''', (date, winner_id, runner_up_id))

    conn.commit()
    conn.close()

    return redirect('/')


# Route to display the "Add Player" page
@app.route('/add_player')
def add_player_page():
    conn = sqlite3.connect('poker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players')
    players = cursor.fetchall()
    conn.close()
    return render_template('add_player.html', players=players)


# Route to handle form submission for adding players
@app.route('/add_player', methods=['POST'])
def add_player():
    name = request.form['name']

    conn = sqlite3.connect('poker.db')
    cursor = conn.cursor()

    # Check if the player already exists
    cursor.execute('SELECT * FROM players WHERE name = ?', (name,))
    existing_player = cursor.fetchone()

    if existing_player:
        # Player already exists, do not add again
        conn.close()
        return redirect('/add_player')

    # Add the new player
    cursor.execute('INSERT INTO players (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

    return redirect('/add_player')


# Route to display the leaderboard
@app.route('/leaderboard')
def leaderboard():
    conn = sqlite3.connect('poker.db')
    cursor = conn.cursor()

    # Fetch the leaderboard data
    cursor.execute('''
    SELECT players.name, SUM(position_points.points) AS total_points
    FROM results
    JOIN players ON results.winner_id = players.id OR results.runner_up_id = players.id
    JOIN position_points ON (results.winner_id = players.id AND position_points.position = results.winner_position)
                         OR (results.runner_up_id = players.id AND position_points.position = results.runner_up_position)
    GROUP BY players.name
    ORDER BY total_points DESC
    ''')
    leaderboard_data = cursor.fetchall()

    conn.close()
    return render_template('leaderboard.html', leaderboard=leaderboard_data, enumerate=enumerate)


if __name__ == '__main__':
    app.run(debug=True)