const socket = io();

let username = "";
let currentCommunity = "";

function fetchCommunities() {
  fetch("/communities")
    .then(res => res.json())
    .then(communities => {
      const list = document.getElementById('communitiesList');
      list.innerHTML = "";
      communities.forEach(comm => {
        let li = document.createElement("li");
        li.textContent = comm;
        li.onclick = () => joinCommunity(comm);
        list.appendChild(li);
      });
    });
}

function addCommunity() {
  const room = document.getElementById('newCommunityName').value.trim();
  if (!room) return;
  fetch("/add_community", {
    method: "POST",
    headers: { 'Content-Type': "application/json" },
    body: JSON.stringify({ room })
  })
    .then(res => res.json())
    .then(d => {
      fetchCommunities();
      document.getElementById('newCommunityName').value = "";
    });
}

function deleteCommunity() {
  if (!currentCommunity) return;
  fetch("/delete_community", {
    method: "POST",
    headers: { 'Content-Type': "application/json" },
    body: JSON.stringify({ room: currentCommunity })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("Community deleted!");
      } else {
        alert("Community not deleted (may not be empty)! " + (data.error || ""));
      }
      leaveCommunity();
      fetchCommunities();
    });
}

function joinCommunity(room) {
  username = document.getElementById('username').value.trim();
  if (!username) {
    alert("Enter your name first");
    return;
  }
  if (currentCommunity) {
    socket.emit('leave', { username, room: currentCommunity });
  }
  document.getElementById('chatWindow').innerHTML = "";
  document.getElementById('chatDiv').style.display = 'block';
  document.getElementById('communityDiv').style.display = 'none';
  document.getElementById('currentCommunity').textContent = "Community: " + room;
  currentCommunity = room;
  socket.emit('join', { username, room });
  document.getElementById('deleteBtn').style.display = "block";
}

function leaveCommunity() {
  if (!currentCommunity) return;
  socket.emit('leave', { username, room: currentCommunity });
  document.getElementById('chatDiv').style.display = 'none';
  document.getElementById('communityDiv').style.display = 'block';
  currentCommunity = "";
  document.getElementById('userList').innerHTML = "";
}

function sendMessage() {
  const msgInput = document.getElementById('chatInput');
  const msg = msgInput.value.trim();
  if (msg && currentCommunity) {
    socket.emit('message', { username, room: currentCommunity, msg });
    msgInput.value = "";
  }
}

socket.on('message', data => {
  const chatWindow = document.getElementById('chatWindow');
  let msgDiv = document.createElement('div');
  msgDiv.textContent = data.msg;
  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
});

socket.on('user_list', users => {
  const userList = document.getElementById('userList');
  userList.innerHTML = '';
  users.forEach(user => {
    const li = document.createElement('li');
    li.textContent = user;
    userList.appendChild(li);
  });
});

// Initial load
window.onload = fetchCommunities;
