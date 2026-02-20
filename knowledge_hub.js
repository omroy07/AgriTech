const socket = io('/knowledge');
let currentCategory = 'General';
let currentSort = 'newest';

document.addEventListener('DOMContentLoaded', () => {
    fetchQuestions();
    fetchTopExperts();

    // Category listeners
    document.querySelectorAll('#kb-categories li').forEach(li => {
        li.addEventListener('click', (e) => {
            document.querySelector('#kb-categories li.active').classList.remove('active');
            e.target.classList.add('active');
            currentCategory = e.target.dataset.cat;
            fetchQuestions();
        });
    });

    // Tab listeners
    document.querySelectorAll('.feed-tabs button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelector('.feed-tabs button.active').classList.remove('active');
            e.target.classList.add('active');
            currentSort = e.target.dataset.sort;
            fetchQuestions();
        });
    });

    // Socket listeners
    socket.emit('join_knowledge_hub', {});
    socket.on('feed_update', (data) => {
        console.log('Hub update:', data);
        // Toast or subtle indicator
    });
});

async function fetchQuestions() {
    const list = document.getElementById('questions-feed');
    list.innerHTML = '<div class="kb-loader">Scanning intelligence...</div>';

    try {
        const url = `/api/v1/questions/?category=${currentCategory}&sort=${currentSort}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.status === 'success') {
            renderQuestions(data.data);
        }
    } catch (error) {
        console.error('Fetch questions failed:', error);
    }
}

function renderQuestions(questions) {
    const list = document.getElementById('questions-feed');
    list.innerHTML = '';

    if (questions.length === 0) {
        list.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--kb-text-muted);">No questions in this category yet. Be the first!</div>';
        return;
    }

    questions.forEach(q => {
        const card = document.createElement('div');
        card.className = 'q-card';
        card.innerHTML = `
            <div class="q-meta">
                <span><i class="fas fa-user"></i> ${q.author}</span>
                <span><i class="fas fa-calendar"></i> ${formatDate(q.created_at)}</span>
                <span><i class="fas fa-tag"></i> ${q.category}</span>
            </div>
            <h2 class="q-title">${q.title}</h2>
            <p style="color: var(--kb-text-muted); font-size: 0.95rem; line-height: 1.5;">${truncate(q.content, 150)}</p>
            <div class="stats-row">
                <div class="stat-item active"><i class="fas fa-thumbs-up"></i> ${q.upvote_count} Votes</div>
                <div class="stat-item"><i class="fas fa-comment"></i> ${q.answer_count} Answers</div>
                <div class="stat-item"><i class="fas fa-eye"></i> ${q.view_count} Views</div>
            </div>
        `;
        card.onclick = () => window.location.href = `/question_detail.html?id=${q.id}`;
        list.appendChild(card);
    });
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString();
}

function truncate(str, len) {
    return str.length > len ? str.substring(0, len) + '...' : str;
}

// Modal logic
document.getElementById('btn-ask-question').onclick = () => {
    document.getElementById('ask-modal').style.display = 'flex';
};

function closeModal() {
    document.getElementById('ask-modal').style.display = 'none';
}

async function submitQuestion() {
    const title = document.getElementById('q-title').value;
    const category = document.getElementById('q-category').value;
    const content = document.getElementById('q-content').value;

    if (!title || !content) return Swal.fire('Error', 'Title and details are required', 'error');

    try {
        const response = await fetch('/api/v1/questions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, category, content })
        });
        const data = await response.json();

        if (data.status === 'success') {
            closeModal();
            Swal.fire('Posted!', 'Your question is now live for experts to see.', 'success');
            fetchQuestions();
        }
    } catch (error) {
        Swal.fire('Error', 'Failed to connect to hub', 'error');
    }
}

async function fetchTopExperts() {
    // Simulated fetching top experts API (not implemented in this turn)
    const list = document.getElementById('top-experts-list');
    const experts = [
        { name: 'Dr. Ramesh', rep: 2450, badges: 8 },
        { name: 'Suresh Patil', rep: 1820, badges: 5 },
        { name: 'Anita Verma', rep: 1640, badges: 4 }
    ];

    list.innerHTML = experts.map(e => `
        <div class="expert-item">
            <div class="expert-avatar">${e.name[0]}</div>
            <div style="flex: 1;">
                <div style="font-weight: 600;">${e.name}</div>
                <div style="font-size: 0.8rem; color: var(--kb-text-muted);">${e.badges} Badges</div>
            </div>
            <div style="font-weight: 700; color: var(--kb-primary);">${e.rep}</div>
        </div>
    `).join('');
}
