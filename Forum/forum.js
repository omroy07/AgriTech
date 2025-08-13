document.getElementById('forumForm').addEventListener('submit', function (e) {
  e.preventDefault();


  const data = {
    name: e.target.name.value,
    message: e.target.message.value
  };


  fetch('http://localhost:5000/forum', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(() => {
      loadPosts();
      e.target.reset();
    });
});


function loadPosts() {
  fetch('http://localhost:5000/forum')
    .then(res => res.json())
    .then(posts => {
      const container = document.getElementById('forumPosts');
      container.innerHTML = '';
      posts.forEach(post => {
        const el = document.createElement('div');
        el.className = 'forum-post';
        el.innerHTML = `<strong>${post.name}</strong>: ${post.message}`;
        container.appendChild(el);
      });
    });
}


document.addEventListener('DOMContentLoaded', loadPosts);



