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
app.config['MYSQL_PASSWORD'] = 'Tarun9392440350'
app.config['MYSQL_DB'] = 'online_assesment'

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



def table_exists(connection, table_name):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES LIKE %s", (table_name,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None   



# home page

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
    


# Teacher operations.......



@app.route('/subject_form')
def subject_form():
    return render_template('subject_form.html')


@app.route('/submit', methods=['POST'])
def submit_subject():
    test_name = request.form['test_name']
    teacher_name = request.form['teacher_name']
    email = request.form['email']
    password = request.form['password']
    Number_of_questions = request.form['Number_of_questions']
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # Fetch the teacher_id based on the provided name, email, and password
            cursor.execute("SELECT teacher_id FROM Teachers WHERE name = %s AND email = %s AND password = %s", (teacher_name, email, password))
            teacher = cursor.fetchone()
            
            if not teacher:
                return jsonify({"error": "Invalid credentials."}), 401
            
            teacher_id = teacher['teacher_id']
            
            # Check if test_name already exists for the teacher
            cursor.execute("SELECT test_name FROM Tests WHERE test_name = %s AND teacher_id = %s", (test_name, teacher_id))
            existing_test = cursor.fetchone()

            if existing_test:
                return jsonify({"error": "Test name already exists. Please choose another name."}), 400

            # Create a new test and get the generated test_id
            cursor.execute("INSERT INTO Tests (teacher_id, test_name, Number_of_questions) VALUES (%s, %s, %s)", (teacher_id, test_name, Number_of_questions))
            connection.commit()
            test_id = cursor.lastrowid

            return redirect(url_for('question_form', test_id=test_id, test_name=test_name))
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

@app.route('/question_form')
def question_form():
    test_name = request.args.get('test_name')
    test_id = request.args.get('test_id')
    return render_template('question_form.html', test_id=test_id, test_name = test_name)

@app.route('/submit_question', methods=['GET','POST'])
def submit_question():
    question = request.form['question']
    option1 = request.form['option1']
    option2 = request.form['option2']
    option3 = request.form['option3']
    option4 = request.form['option4']
    correct_option = request.form['correct_option']
    tag = request.form['tag']
    test_id = request.args.get('test_id')

    print(f"Submitted test_id: {test_id}")

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO Test_Questions (question, option1, option2, option3, option4, correct_option, tag, test_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (question, option1, option2, option3, option4, correct_option, tag, test_id)
            )
            connection.commit()
            print("Question data inserted successfully.")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

    return redirect(url_for('question_form', test_id=test_id))


@app.route('/finish', methods=['POST'])
def finish():
    return redirect(url_for('role_selection'))


# Student operations....

@app.route('/subject_input')
def subject_input():
    return render_template('subject_input.html')

@app.route('/student_quiz', methods=['GET'])
def student_quiz():
    Test_name = request.args.get('Test_name')
    print(Test_name)
    return redirect(url_for('index',Test_name=Test_name))



@app.route('/questions', methods=['GET'])
def get_questions():
    test_name = request.args.get('Test_name')
    tag = request.args.get('tag', 'easy')
    limit = int(request.args.get('limit', 5))
    
    if not test_name:
        return jsonify({'msg': 'Test name not provided or invalid.'}), 400
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Check if test_name exists in Tests table to determine if it's a custom test
        cursor.execute("SELECT test_id FROM Tests WHERE test_name = %s", (test_name,))
        test = cursor.fetchone()
        
        if test:
            # If test_id exists, retrieve questions from Test_Questions table
            test_id = test['test_id']
            query = "SELECT * FROM Test_Questions WHERE test_id = %s AND tag = %s ORDER BY RAND() LIMIT %s"
            cursor.execute(query, (test_id, tag, limit))
        else:
            # If test_id does not exist, retrieve questions from the predefined table
            query = f"SELECT * FROM `{test_name}` WHERE tag = %s ORDER BY RAND() LIMIT %s"
            cursor.execute(query, (tag, limit))
        
        questions = cursor.fetchall()
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
        
        return jsonify(formatted_questions)
    
    return jsonify({'msg': 'Failed to connect to database'})



@app.route('/index')
def index():
    Test_name = request.args.get('Test_name')
    print(Test_name,"Index file")

    return render_template('index.html', Test_name=Test_name)

# Results......

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


# Displaying the feedback...

@app.route('/performance')
def performance():
    graph_path = request.args.get('graph')
    feedback = request.args.get('feedback')
    score = request.args.get('score')
    return render_template('performance.html', graph_path=graph_path, feedback=feedback, score=score)



if __name__ == '__main__':
    app.run(debug=True)

