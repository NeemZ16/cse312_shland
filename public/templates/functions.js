function welcome() {
    document.getElementById("paragraph").innerHTML += "<br/>JavaScript text is so 😀 🤯 🤯 🤯 🤯 🤯 🤯 🤯 🤯 🤯 🤯 🤯"


    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });

    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 😀";

    updatePosts();
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

function clearPosts() {
    const postList = document.getElementById('post-list');
    postList.innerHTML = '';
}

function addPost(post) {
    const postList = document.getElementById('post-list');
    const postItem = document.createElement('li');
    var postID = post.id // record post id

    var likeButton = document.createElement('input'); // create like button
    likeButton.type = 'checkbox';
    likeButton.id = postID;
    likeButton.checked = False;
    postItem.appendChild(likeButton) // append cb to li

    postItem.innerText = `${post.username}: ${post.title} - ${post.description}`;
    postList.appendChild(postItem);
}