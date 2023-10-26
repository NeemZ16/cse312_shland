function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });

    updatePosts();
    updateQuizQuestions();
    console.log("yes");
    setInterval(updatePosts, 2000);
}
function updatePosts() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearPosts();
            const posts = JSON.parse(this.response);
            console.log(posts)
            for (const post of posts) {
                addPost(post);
            }
        }
    };
    request.open("GET", "/get-posts");
    request.send();
}

function updateQuizQuestions() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearQuiz();
            const questions = JSON.parse(this.response);
            console.log(questions)
            for (const question of questions) {
                addQuestion(question);
            }
        }
    };
    request.open("GET", "/get-quiz");
    request.send();
}

function clearPosts() {
    const postList = document.getElementById('post-list');
    postList.innerHTML = '';
}

function clearQuiz() {
    const questions = document.getElementById('quiz-list');
    questions.innerHTML = '';
}

function addPost(post) {
    const postList = document.getElementById('post-list');
    const postItem = document.createElement('li');
    postItem.innerText = `${post.username}: ${post.title} - ${post.description} - likes: ${post.likecount}`;
    postList.appendChild(postItem);

    var postID = post._id // record post id
    // var likeCount = post.likeCount;
    var likeButton = document.createElement('button'); // create like button
    likeButton.innerHTML = 'like post above';
    // likeButton.type = 'button'; // may not be necessary
    likeButton.name = 'like-button';
    likeButton.value = postID;
    // likeButton.onclick = likePost(likeButton);
    likeButton.addEventListener("click", function () {likePost(likeButton)});
    postList.appendChild(likeButton) // append cb to li
}

function addQuestion(question) {
    const questionList = document.getElementById('quiz-list');
    const questionItem = document.createElement('li');
    questionItem.innerText = `${question.title}`;
    questionList.appendChild(questionItem);
}

function likePost(likeButton) {
    const request = new XMLHttpRequest();
    request.open("POST", "/like-post");
    const postID = likeButton.value;
    const body = JSON.stringify({'_id': postID}); // is this enough? we valid them in the python file
    request.send(body);
}
