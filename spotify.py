from flask import Flask, render_template, request


app = Flask(__name__)

@app.route('/')

def index():
    return render_template('front_page.html')

@app.route('/playlist_select')
def playlist_select():
    return render_template('playlist_select.html')

@app.route('/main_page')
def main_page():
    return render_template('main_page.html')



@app.route('/guesses', methods=['POST'])
def handle_guesses():
    input_title_guess = request.form.get('title_guess')  
    input_artist_guess = request.form.get('artist_guess')
    return f'Your guess, {input_title_guess} by {input_artist_guess}!'

if __name__ == "__main__":
    app.run(debug = True, port = 5001)