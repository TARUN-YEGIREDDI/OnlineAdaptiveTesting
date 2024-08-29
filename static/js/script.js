 document.addEventListener('DOMContentLoaded', () => {
    const questionElement = document.getElementById('question');
    const answerButtonsElement = document.getElementById('answer-buttons');
    const nextButton = document.getElementById('next-btn');
    const scoreContainer = document.getElementById('score-container');
    const playAgainButton = document.getElementById('play-again-btn');
    const questionNumberElement = document.getElementById('question-number');
    const tagElement = document.getElementById('tag');
    let currentQuestionIndex, score, totalQuestionsAsked, questions, easyQuestions, mediumQuestions, hardQuestions;
    let usedQuestions = new Set();
    const appDiv = document.querySelector('.app');
    const TestName = appDiv.getAttribute('data-subject-name');
    const totalQuestions = parseInt(appDiv.getAttribute('data-no-of-questions'));
    const perform = document.getElementById('performance');
    const performanceGraph = document.getElementById('performance-graph');
    let wrongquestions = [];
    let correctquestions = [];
    let result = [0, 0, 0, 0, 0, 0];
    let flag = 0;
    let tag_name = "";

// percentage of questions for each difficulty level
    const easyPercentage = 40;
    const mediumPercentage = 35;
    const hardPercentage = 25;

    easyQuestions = Math.ceil(totalQuestions * (easyPercentage / 100));
    mediumQuestions = Math.round(totalQuestions * (mediumPercentage / 100));
    hardQuestions = Math.round(totalQuestions * (hardPercentage / 100));

    // Adjust counts to ensure the total is correct
    while (easyQuestions + mediumQuestions + hardQuestions !== totalQuestions) {
        const difference = totalQuestions - (easyQuestions + mediumQuestions + hardQuestions);
    
        if (difference > 0) {
            // Increase medium or hard questions to match the totalQuestions
            if (mediumQuestions <= hardQuestions) {
                mediumQuestions += 1;
            } else {
                hardQuestions += 1;
            }
        } else {
            // Decrease medium or hard questions to match the totalQuestions
            if (mediumQuestions >= hardQuestions) {
                mediumQuestions -= 1;
            } else {
                hardQuestions -= 1;
            }
        }
    }


// Start the quiz 
    function startQuiz() {
        score = 0;
        perform.style.display = "none";
        performanceGraph.classList.add('hidden');
        result = [0, 0, 0, 0, 0, 0];
        tag_name = "";
        totalQuestionsAsked = 0;
        usedQuestions.clear();
        scoreContainer.classList.add('hidden');
        fetchQuestions('easy', easyQuestions);
    }
    
// Fetch questions from the server
    function fetchQuestions(tag, limit) {
        tag_name = tag;
        return fetch(`/questions?Test_name=${TestName}&tag=${tag}&limit=${limit}`)
            .then(response => response.json())
            .then(data => {
                data = data.filter(question => !usedQuestions.has(question.text));
                questions = data;
                questions.forEach(question => usedQuestions.add(question.text));
                currentQuestionIndex = 0;
                setNextQuestion();
            });
    }

// Set the next question
    function setNextQuestion() {
        resetState();
        if (questions && questions.length > 0) {
            showQuestion(questions[currentQuestionIndex]);
        } else {
            adjustDifficultyAndContinue();
        }
    }

    // Reset the state of the question
    function resetState() {
        nextButton.classList.add('hidden');
        while (answerButtonsElement.firstChild) {
            answerButtonsElement.removeChild(answerButtonsElement.firstChild);
        }
    }



// Display the question
    function showQuestion(question) {
        questionNumberElement.innerText = ` ${totalQuestionsAsked + 1})`;
        questionElement.innerText = question.text;
        tagElement.innerText = tag_name;
        answerButtonsElement.innerHTML = '';

        question.answers.forEach(answer => {
            const button = document.createElement('button');
            button.innerText = answer.text;
            button.classList.add('btn');
            if (answer.correct) {
                button.dataset.correct = answer.correct;
            }
            button.addEventListener('click', (e) => selectAnswer(e, question));
            answerButtonsElement.appendChild(button);
        });
    }


// To store the correct and wrong questions based on the user's response
    function selectAnswer(e, question) {
        const selectedButton = e.target;
        const correct = selectedButton.dataset.correct === 'true';
        if (correct) {
            score++;
            if (tag_name == "easy")
                result[1] = result[1] + 1;
            else if (tag_name == "medium")
                result[3] = result[3] + 1;
            else if (tag_name == "hard")
                result[5] = result[5] + 1;
        } else {
            if (tag_name == "easy") {
                result[0] = result[0] + 1;
            } else if (tag_name == "medium") {
                result[2] = result[2] + 1;
            } else if (tag_name == "hard") {
                result[4] = result[4] + 1;
            }
            wrongquestions.push(question.text); // Store the question text
        }
        Array.from(answerButtonsElement.children).forEach(button => {
            setStatusClass(button, button.dataset.correct === 'true', selectedButton);
        });
        nextButton.classList.remove('hidden');
    }

    // Set the status of the answer based on the user's response
    function setStatusClass(element, correct, selectedButton) {
        clearStatusClass(element);
        if (correct) {
            element.classList.add('correct');
        } else if(element === selectedButton) {
            element.classList.add('incorrect');
        }
    }

    // Clear the status of the answer
    function clearStatusClass(element) {
        element.classList.remove('correct');
        element.classList.remove('incorrect');
    }

    
// Adjust the difficulty level based on the user's performance
    function adjustDifficultyAndContinue() {
        if (totalQuestionsAsked >= totalQuestions) {
            showScore();
        } else if (totalQuestionsAsked >= easyQuestions + mediumQuestions) {
            const marks = score;
            const percentage = (marks / (easyQuestions + mediumQuestions)) * 100;
            if (percentage >= 70 && flag ===1) {
                console.log(flag);
                fetchQuestions('hard', hardQuestions);
            } else if (percentage >= 60 && percentage < 70) {
                fetchQuestions('medium', hardQuestions);
            } else {
                fetchQuestions('easy', hardQuestions);
            }
        } else if (totalQuestionsAsked >= easyQuestions) {
            const easyMarks = score;
            const percentage = (easyMarks / easyQuestions) * 100;
            if (percentage >= 70) {
                fetchQuestions('medium', mediumQuestions);
                flag = 1;
                console.log(flag);
            } else {
                fetchQuestions('easy', mediumQuestions);
            }
        }
    }


// Display the score
    function showScore() {
        const scoreContainer = document.getElementById('score-container');
        scoreContainer.classList.remove('hidden');
        document.getElementById('score-text').innerText = `Your Score: ${score}`;

        perform.style.display = "block";
        perform.removeEventListener('click', performanceClickHandler);
        perform.addEventListener('click', performanceClickHandler);
    }

    // Submit the results to the server and display the performance
    function performanceClickHandler(e) {
        fetch('/submit_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ results: result, wrongQuestions: wrongquestions, correctQuestions: correctquestions })
        })
        .then(response => response.json())
        .then(data => {
            window.location.href = `/performance?graph=${data.address}&feedback=${data.feedback}&score=${score}`;
        });
    }
    
    
// next button event listener
    nextButton.addEventListener('click', () => {
        currentQuestionIndex++;
        totalQuestionsAsked++;
        if (totalQuestionsAsked >= totalQuestions) {
            showScore();
        } else if (currentQuestionIndex >= questions.length) {
            adjustDifficultyAndContinue();
        } else {
            setNextQuestion();
        }
    });

    // play again button event listener
    playAgainButton.addEventListener('click', () => {
        startQuiz();
    });

    // startQuiz function call to start the quiz
    startQuiz();
});

