 document.addEventListener('DOMContentLoaded', () => {
    const questionElement = document.getElementById('question');
    const answerButtonsElement = document.getElementById('answer-buttons');
    const nextButton = document.getElementById('next-btn');
    const scoreContainer = document.getElementById('score-container');
    const playAgainButton = document.getElementById('play-again-btn');
    const questionNumberElement = document.getElementById('question-number');
    const tagElement = document.getElementById('tag');
    let currentQuestionIndex, score, totalQuestionsAsked, questions;
    let usedQuestions = new Set();
    const appDiv = document.querySelector('.app');
    const TestName = appDiv.getAttribute('data-subject-name');
    const perform = document.getElementById('performance');
    const performanceGraph = document.getElementById('performance-graph');
    let wrongquestions = [];
    let result = [0, 0, 0, 0, 0, 0];

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

    function startQuiz() {
        score = 0;
        perform.style.display = "none";
        performanceGraph.classList.add('hidden');
        result = [0, 0, 0, 0, 0, 0];
        tag_name = "";
        totalQuestionsAsked = 0;
        usedQuestions.clear();
        scoreContainer.classList.add('hidden');
        fetchQuestions('easy', 5);
    }

    function setNextQuestion() {
        resetState();
        if (questions && questions.length > 0) {
            showQuestion(questions[currentQuestionIndex]);
        } else {
            adjustDifficultyAndContinue();
        }
    }

    function showQuestion(question) {
        questionNumberElement.innerText = ` ${totalQuestionsAsked + 1}`;
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

    function resetState() {
        nextButton.classList.add('hidden');
        while (answerButtonsElement.firstChild) {
            answerButtonsElement.removeChild(answerButtonsElement.firstChild);
        }
    }

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
            setStatusClass(button, button.dataset.correct === 'true');
        });
        nextButton.classList.remove('hidden');
    }

    function setStatusClass(element, correct) {
        clearStatusClass(element);
        if (correct) {
            element.classList.add('correct');
        } else {
            element.classList.add('incorrect');
        }
    }

    function clearStatusClass(element) {
        element.classList.remove('correct');
        element.classList.remove('incorrect');
    }

    function adjustDifficultyAndContinue() {
        if (totalQuestionsAsked >= 10) {
            showScore();
        } else if (totalQuestionsAsked >= 8) {
            if (score >= 7) {
                fetchQuestions('hard', 2);
            } else if (score === 6) {
                fetchQuestions('medium', 2);
            } else {
                fetchQuestions('easy', 2);
            }
        } else if (totalQuestionsAsked >= 5) {
            if (score >= 4) {
                fetchQuestions('medium', 3);
            } else {
                fetchQuestions('easy', 3);
            }
        }
    }

    function showScore() {
        const scoreContainer = document.getElementById('score-container');
        scoreContainer.classList.remove('hidden');
        document.getElementById('score-text').innerText = `Your Score: ${score}`;

        perform.style.display = "block";
        perform.removeEventListener('click', performanceClickHandler);
        perform.addEventListener('click', performanceClickHandler);
    }

    function performanceClickHandler(e) {
        fetch('/submit_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ results: result, wrongQuestions: wrongquestions })
        })
        .then(response => response.json())
        .then(data => {
            window.location.href = `/performance?graph=${data.address}&feedback=${data.feedback}&score=${score}`;
        });
    }
    
    

    nextButton.addEventListener('click', () => {
        currentQuestionIndex++;
        totalQuestionsAsked++;
        if (totalQuestionsAsked >= 10) {
            showScore();
        } else if (currentQuestionIndex >= questions.length) {
            adjustDifficultyAndContinue();
        } else {
            setNextQuestion();
        }
    });

    playAgainButton.addEventListener('click', () => {
        startQuiz();
    });

    startQuiz();
});

