from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import io, os
import base64
import google.generativeai as genai

app = Flask(__name__)

# Configuration for MySQL database
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lokesh@2004'
app.config['MYSQL_DB'] = 'questions'

# Configure Google Generative AI
api_key = 'AIzaSyAartIcl8H5Uax4PI-msaiDlCqI2RBMEzg'
genai.configure(api_key=api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        if connection.is_connected():
            print("Connection to MySQL established successfully.")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def create_table(subject_name):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            table_creation_query = f"""
            CREATE TABLE IF NOT EXISTS `{subject_name}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question VARCHAR(255) NOT NULL,
                option1 VARCHAR(255) NOT NULL,
                option2 VARCHAR(255) NOT NULL,
                option3 VARCHAR(255) NOT NULL,
                option4 VARCHAR(255) NOT NULL,
                correct_option VARCHAR(255) NOT NULL,
                tag VARCHAR(50) NOT NULL
            )"""
            cursor.execute(table_creation_query)
            connection.commit()
            print(f"Table `{subject_name}` created successfully.")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

@app.route('/')
def role_selection():
    return render_template('role_selection.html')

@app.route('/role_redirect', methods=['POST'])
def role_redirect():
    role = request.form['role']
    if role == 'teacher':
        return redirect(url_for('subject_form'))
    elif role == 'student':
        return redirect(url_for('subject_input'))
    else:
        return redirect(url_for('role_selection'))

@app.route('/subject_form')
def subject_form():
    return render_template('subject_form.html')

@app.route('/submit', methods=['POST'])
def submit_subject():
    subject_name = request.form['subject_name']
    create_table(subject_name)
    return redirect(url_for('question_form', subject_name=subject_name))

@app.route('/question_form')
def question_form():
    subject_name = request.args.get('subject_name')
    return render_template('question_form.html', subject_name=subject_name)

@app.route('/submit_question', methods=['POST'])
def submit_question():
    question = request.form['question']
    option1 = request.form['option1']
    option2 = request.form['option2']
    option3 = request.form['option3']
    option4 = request.form['option4']
    correct_option = request.form['correct_option']
    tag = request.form['tag']
    subject_name = request.form['subject_name']

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"INSERT INTO `{subject_name}` (question, option1, option2, option3, option4, correct_option, tag) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (question, option1, option2, option3, option4, correct_option, tag)
            )
            connection.commit()
            print("Question data inserted successfully.")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

    return redirect(url_for('question_form', subject_name=subject_name))

@app.route('/finish', methods=['POST'])
def finish():
    return redirect(url_for('role_selection'))

@app.route('/subject_input')
def subject_input():
    return render_template('subject_input.html')

@app.route('/student_quiz', methods=['POST'])
def student_quiz():
    subject_name = request.form['subject_name']
    print(subject_name)
    return redirect(url_for('index',subject_name=subject_name))

@app.route('/questions', methods=['GET'])
def get_questions():
    subject_name = request.args.get('subject_name')
    tag = request.args.get('tag', 'easy')
    limit = int(request.args.get('limit', 5))
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        print(subject_name)
        query = f"SELECT * FROM `{subject_name}` WHERE tag = %s ORDER BY RAND() LIMIT %s"
        cursor.execute(query, (tag, limit))
        questions = cursor.fetchall()
        print("Vaar")
        formatted_questions = []
        for question in questions:
            formatted_question = {
                "text": question["question"],
                "answers": [
                    {"text": question["option1"], "correct": question["correct_option"] == "option1"},
                    {"text": question["option2"], "correct": question["correct_option"] == "option2"},
                    {"text": question["option3"], "correct": question["correct_option"] == "option3"},
                    {"text": question["option4"], "correct": question["correct_option"] == "option4"}
                ]
            }
            formatted_questions.append(formatted_question)
        cursor.close()
        connection.close()
        print(formatted_questions)  # Debugging: print the formatted questions
        
        return jsonify(formatted_questions)
    
    return jsonify({'msg': 'Failed to connect to database'})

@app.route('/index')
def index():
    subject_name = request.args.get('subject_name')
    print(subject_name,"Index file")

    return render_template('index.html', subject_name=subject_name)

@app.route('/submit_results', methods=['POST'])
def submit_results():
    data = request.json
    results = data.get('results', [])
    wrong_questions = data.get('wrongQuestions', [])

    # Generate the graph
    categories = ['Easy', 'Medium', 'Hard']
    wrong_answers = [results[0], results[2], results[4]]
    right_answers = [results[1], results[3], results[5]]

    # Generate the bar graph
    x = range(len(categories))
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar(x, wrong_answers, width=0.4, label='Wrong Answers', align='center', color="r")
    ax.bar(x, right_answers, width=0.4, label='Right Answers', align='edge', color="green")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_xlabel('Difficulty Level')
    ax.set_ylabel('Number of Answers')
    ax.set_title('Performance by Difficulty Level')
    ax.legend()

    save_folder = os.path.join(os.getcwd(), 'static', 'images')
    os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist
    save_path = os.path.join(save_folder, 'performance_graph.png')

    # Save the graph to the specified folder
    plt.savefig(save_path)

    # Generate feedback using Google Generative AI
    prompt = f"""
    You are a teacher who gives feedback based on some assessment parameters.
    All questions have the same score. For now, use the below scores and give feedback. 
    Total questions are 10.
    I have written the exam and the details are:
    easy questions = {results[1] + results[0]}, score = {results[1]}
    medium questions = {results[3] + results[2]}, score = {results[3]}
    hard questions = {results[5] + results[4]}, score = {results[5]}
    
    The questions I got wrong are: {', '.join(wrong_questions)}
    analyze all the wrong questions and give generalized feedback.
    give it in a paragraph manner which consists of 10 senences.
    """
    response = model.generate_content(prompt)
    feedback = response.text

    return jsonify({'address': r"static\images\performance_graph.png", 'feedback': feedback})

@app.route('/performance')
def performance():
    graph_path = request.args.get('graph')
    feedback = request.args.get('feedback')
    score = request.args.get('score')
    return render_template('performance.html', graph_path=graph_path, feedback=feedback, score=score)



if __name__ == '__main__':
    app.run(debug=True)

