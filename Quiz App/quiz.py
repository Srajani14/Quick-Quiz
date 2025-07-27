from flask import Flask, render_template, request, redirect, url_for, session
import csv, os, random

app = Flask(__name__)
app.secret_key = 'secret_key'  # Secret key

# Load available quiz topics
def list_files(folder):
    return [f for f in os.listdir(folder) if f.endswith('.csv')]    #loads the file ending with CSV

# Load quiz questions
def load_questions(file_path):
    questions = []                  #empty list
    with open(file_path, encoding='utf-8') as file:     #opens the file
        reader = csv.DictReader(file)                   #Reads the csv file as dictionary
        for row in reader:                              
            questions.append({                          #Appending
                'question': row['question'],
                'options': [row['option1'], row['option2'], row['option3'], row['option4']],
                'answer': row['answer']
            })
    return questions

# Save result
def save_score(username, topic, score, total):          #Save to csv file
    with open('scores.csv', 'a', newline='') as file:   #Open csv file
        writer = csv.writer(file)                       #Writing to file
        writer.writerow([username, topic, score, total])

@app.route('/')
def home():
    topics = [f.replace('.csv', '') for f in list_files('Questions')]   #Calls list file function 
    return render_template('home.html', topics=topics)

@app.route('/start', methods=['POST'])
def start():
    username = request.form['username']
    topic = request.form['topic']
    questions = load_questions(f'Questions/{topic}.csv')
    random.shuffle(questions)           #Shuffle question
    session['username'] = username
    session['topic'] = topic
    session['questions'] = questions
    session['score'] = 0
    session['current'] = 0
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        answer = request.form.get('answer')
        current = session['current']
        correct_answer = session['questions'][current]['answer']
        if answer == correct_answer:
            session['score'] += 1
        session['current'] += 1

    current = session['current']
    if current >= len(session['questions']):
        return redirect(url_for('result'))

    q = session['questions'][current]
    options = q['options']
    random.shuffle(options)
    return render_template('quiz.html', question=q['question'], options=options)

@app.route('/result')
def result():
    username = session['username']
    topic = session['topic']
    score = session['score']
    total = len(session['questions'])
    save_score(username, topic, score, total)
    return render_template('result.html', score=score, total=total, user=username, topic=topic)

if __name__ == '__main__':
    app.run(debug=True)
