document.getElementById('forumForm').addEventListener('submit', function (e) {
  e.preventDefault();

  // Create data object matching the HTML form names and Python backend expectations
  const data = {
    title: document.getElementById('title').value,
    author: document.getElementById('author').value,
    content: document.getElementById('content').value,
    timestamp: new Date().toISOString() // Add client-side timestamp
  };

  const submitBtn = e.target.querySelector('button[type="submit"]');
  const originalText = submitBtn.innerHTML;
  submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';
  submitBtn.disabled = true;

  fetch('http://localhost:5000/forum', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(res => {
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    })
    .then(() => {
      loadPosts();
      e.target.reset();
      // Show simple success feedback (optional)
      alert('Post created successfully!');
    })
    .catch(err => {
      console.error('Error:', err);
      alert('Failed to create post. Please try again.');
    })
    .finally(() => {
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;
    });
});

function loadPosts() {
  const container = document.getElementById('forumPosts');
  
  fetch('http://localhost:5000/forum')
    .then(res => res.json())
    .then(posts => {
      container.innerHTML = '';
      
      if (posts.length === 0) {
        container.innerHTML = `
          <div style="text-align: center; padding: 2rem; color: #64748b; background: white; border-radius: 12px; border: 1px dashed #cbd5e1;">
            <i class="fas fa-comments" style="font-size: 2rem; margin-bottom: 1rem; color: #cbd5e1;"></i>
            <p>No discussions yet. Be the first to start one!</p>
          </div>`;
        return;
      }

      // Show newest first
      posts.reverse().forEach(post => {
        const el = document.createElement('div');
        el.className = 'forum-post';
        
        // Handle missing data gracefully
        const title = post.title || 'Untitled Discussion';
        const author = post.author || post.name || 'Anonymous'; // Fallback for old data
        const content = post.content || post.message || ''; // Fallback for old data
        
        el.innerHTML = `
          <div class="post-meta">
            <div class="author-avatar">
              <i class="fas fa-user"></i>
            </div>
            <strong>${escapeHtml(author)}</strong>
            <span>•</span>
            <span>Just now</span>
          </div>
          <h3 class="post-title">${escapeHtml(title)}</h3>
          <div class="post-content">
            ${escapeHtml(content)}
          </div>
        `;
        container.appendChild(el);
      });
    })
    .catch(err => {
      container.innerHTML = `<p style="color: red; text-align: center;">Error loading posts. Is the backend running?</p>`;
      console.error(err);
    });
}

// Helper to prevent XSS
function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

document.addEventListener('DOMContentLoaded', loadPosts);