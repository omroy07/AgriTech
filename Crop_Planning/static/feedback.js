// Centralized feedback component for user messages (success, error, info)
// Usage: showFeedback('Message', 'error'|'success'|'info')

function showFeedback(message, type = 'info') {
  let feedback = document.getElementById('feedback-message');
  if (!feedback) {
    feedback = document.createElement('div');
    feedback.id = 'feedback-message';
    feedback.style.position = 'fixed';
    feedback.style.top = '20px';
    feedback.style.left = '50%';
    feedback.style.transform = 'translateX(-50%)';
    feedback.style.zIndex = '9999';
    feedback.style.minWidth = '250px';
    feedback.style.maxWidth = '90vw';
    feedback.style.padding = '1rem 1.5rem';
    feedback.style.borderRadius = '8px';
    feedback.style.fontSize = '1.1rem';
    feedback.style.boxShadow = '0 2px 12px rgba(0,0,0,0.15)';
    feedback.style.textAlign = 'center';
    feedback.style.transition = 'opacity 0.3s';
    feedback.style.opacity = '0.98';
    document.body.appendChild(feedback);
  }
  feedback.textContent = message;
  if (type === 'error') {
    feedback.style.background = '#ffebee';
    feedback.style.color = '#c62828';
    feedback.style.border = '1px solid #c62828';
  } else if (type === 'success') {
    feedback.style.background = '#e8f5e9';
    feedback.style.color = '#2e7d32';
    feedback.style.border = '1px solid #2e7d32';
  } else {
    feedback.style.background = '#e3f2fd';
    feedback.style.color = '#1565c0';
    feedback.style.border = '1px solid #1565c0';
  }
  feedback.style.display = 'block';
  feedback.style.opacity = '0.98';
  setTimeout(() => {
    feedback.style.opacity = '0';
    setTimeout(() => {
      feedback.style.display = 'none';
    }, 400);
  }, 3500);
}

// Example usage:
// showFeedback('This is an error!', 'error');
// showFeedback('Operation successful!', 'success');
// showFeedback('This is an info message.');
