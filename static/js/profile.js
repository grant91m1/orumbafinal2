// Profile JavaScript - Glass UI Dynamic Dashboard
class ProfileApp {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.loadUserInfo();
        this.bindEvents();
        this.switchSection('dashboard');
        this.loadStats();
    }

    loadUserInfo() {
        fetch('/api/check-auth')
            .then(res => res.json())
            .then(data => {
                if (data.authenticated) {
                    this.currentUser = data;
                    document.getElementById('user-name').textContent = data.username;
                    const roleEl = document.getElementById('user-role');
                    roleEl.textContent = 'Citizen'; // From session or API
                }
            });
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-link:not(.dropdown a)').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.closest('a').dataset.section;
                this.switchSection(section);
            });
        });

        // Dropdowns
        document.querySelectorAll('.dropdown > a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const dropdown = e.currentTarget.parentElement;
                dropdown.classList.toggle('open');
            });
        });

        // Modals
        document.querySelectorAll('.modal-close, .glass-modal').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-close') || e.target.classList.contains('glass-modal')) {
                    this.closeModal(e.target.closest('.glass-modal'));
                }
            });
        });

        // Forms
        const postForm = document.getElementById('post-form');
        if (postForm) postForm.addEventListener('submit', (e) => this.handlePostSubmit(e));
        const albumForm = document.getElementById('album-form');
        if (albumForm) albumForm.addEventListener('submit', (e) => this.handleAlbumSubmit(e));
        const eventForm = document.getElementById('event-form');
        if (eventForm) eventForm.addEventListener('submit', (e) => this.handleEventSubmit(e));
        const settingsForm = document.getElementById('settings-form');
        if (settingsForm) settingsForm.addEventListener('submit', (e) => this.handleSettingsSubmit(e));

        // Logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) logoutBtn.addEventListener('click', () => {
            fetch('/api/logout', {method: 'POST'}).then(() => location.href = '/');
        });
    }

    switchSection(section) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

        // Show selected
        const targetSection = document.getElementById(section);
        if (targetSection) targetSection.classList.add('active');
        const targetLink = document.querySelector(`[data-section="${section}"]`);
        if (targetLink) targetLink.classList.add('active');

        // Load data
        switch(section) {
            case 'dashboard': this.loadStats(); break;
            case 'posts': this.loadPosts(); break;
            case 'albums': this.loadAlbums(); break;
            case 'events': this.loadEvents(); break;
            case 'settings': this.loadSettings(); break;
        }
    }

    loadStats() {
        fetch('/api/profile/stats')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    const statPosts = document.getElementById('stat-posts');
                    if (statPosts) statPosts.textContent = data.stats.posts;
                    const statAlbums = document.getElementById('stat-albums');
                    if (statAlbums) statAlbums.textContent = data.stats.albums;
                    const statEvents = document.getElementById('stat-events');
                    if (statEvents) statEvents.textContent = data.stats.events;
                }
            });
    }

    loadPosts() {
        fetch('/api/profile/posts')
            .then(res => res.json())
            .then(data => {
                console.log('Posts data:', data); // Debug
                if (data.status === 'success') {
                    this.renderPosts(data.posts, 'posts-grid');
                } else {
                    document.getElementById('posts-grid').innerHTML = '<p class="no-data">No posts yet. <a href="/create-post">Create one</a></p>';
                }
            }).catch(err => {
                console.error('Load posts error:', err);
                document.getElementById('posts-grid').innerHTML = '<p class="no-data">Error loading posts.</p>';
            });
    }

    renderPosts(posts, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = posts.map(post => `
            <div class="content-card glass-card">
                ${post.image ? `<img src="${post.image}" alt="Cover" style="max-height: 200px; object-fit: cover;">` : ''}
                <div class="card-body">
                    <h4>${post.title || 'Untitled'}</h4>
                    <p>${(post.content || '').substring(0, 100)}...</p>
                    <span class="status-badge ${post.status || 'draft'}">${(post.status || 'draft').toUpperCase()}</span>
                    <div class="card-actions">
                        <button class="btn-glass edit-post" data-id="${post.id}">Edit</button>
                        <button class="btn-glass delete-post" data-id="${post.id}">Delete</button>
                    </div>
                </div>
            </div>
        `).join('') || '<p class="no-data">No posts yet. <a href="/create-post">Create one</a></p>';

        // Bind delete actions
        container.querySelectorAll('.delete-post').forEach(btn => {
            btn.addEventListener('click', (e) => this.deletePost(e.target.dataset.id));
        });
    }

    loadAlbums() {
        fetch('/api/profile/albums')
            .then(res => res.json())
            .then(data => {
                console.log('Albums data:', data); // Debug
                if (data.status === 'success') {
                    this.renderAlbums(data.albums, 'albums-grid');
                } else {
                    document.getElementById('albums-grid').innerHTML = '<p class="no-data">No albums yet.</p>';
                }
            });
    }

    renderAlbums(albums, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = albums.map(album => `
            <div class="content-card glass-card">
                ${album.posts && album.posts[0]?.image_url ? `<img src="${album.posts[0].image_url}" alt="Cover">` : ''}
                <div class="card-body">
                    <h4>${album.title || 'Untitled'}</h4>
                    <p>${album.posts ? album.posts.length : 0} images</p>
                    <div class="card-actions">
                        <button class="btn-glass view-album" data-id="${album.id}">View</button>
                        <button class="btn-glass delete-album" data-id="${album.id}">Delete</button>
                    </div>
                </div>
            </div>
        `).join('') || '<p class="no-data">No albums yet.</p>';
    }

    loadEvents() {
        fetch('/api/profile/events')
            .then(res => res.json())
            .then(data => {
                console.log('Events data:', data); // Debug
                if (data.status === 'success') {
                    this.renderEvents(data.events, 'events-grid');
                } else {
                    document.getElementById('events-grid').innerHTML = '<p class="no-data">No events yet.</p>';
                }
            });
    }

    renderEvents(events, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = events.map(event => `
            <div class="content-card glass-card">
                ${event.image ? `<img src="${event.image}" alt="Event" style="max-height: 150px; object-fit: cover;">` : ''}
                <div class="card-body">
                    <h4>${event.title || 'Untitled'}</h4>
                    <p>${event.datetime ? new Date(event.datetime).toLocaleString() : ''}</p>
                    <p>${event.location || ''}</p>
                    <div class="card-actions">
                        <button class="btn-glass edit-event" data-id="${event.id}">Edit</button>
                        <button class="btn-glass delete-event" data-id="${event.id}">Delete</button>
                    </div>
                </div>
            </div>
        `).join('') || '<p class="no-data">No events yet. <a href="/create-event">Create one</a></p>';
    }

    loadSettings() {
        // Load user profile data
        fetch('/api/check-auth').then(res => res.json()).then(data => {
            if (data.authenticated) {
                const user = data; // Enhanced if needed
                document.getElementById('user-name-input').value = user.name || '';
                document.getElementById('user-email-input').value = user.email || '';
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    async deletePost(postId) {
        if (confirm('Delete this post?')) {
            const res = await fetch(`/api/profile/posts/${postId}`, {method: 'DELETE'});
            if (res.ok) {
                this.loadPosts();
                this.loadStats();
            }
        }
    }

    async deleteAlbum(albumId) {
        if (confirm('Delete album?')) {
            // API call
            this.loadAlbums();
            this.loadStats();
        }
    }

    async deleteEvent(eventId) {
        if (confirm('Delete event?')) {
            // API call
            this.loadEvents();
            this.loadStats();
        }
    }

    async handlePostSubmit(e) {
        // Modal-based only if exists
        console.log('Post submit');
    }

    async handleAlbumSubmit(e) {
        console.log('Album submit');
    }

    async handleEventSubmit(e) {
        console.log('Event submit');
    }

    async handleSettingsSubmit(e) {
        e.preventDefault();
        const formData = {
            name: document.getElementById('user-name-input').value,
            email: document.getElementById('user-email-input').value
        };
        const res = await fetch('/api/profile/settings', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        if (res.ok) {
            this.showNotification('Settings saved!');
            this.loadUserInfo();
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch('/api/upload/image', {method: 'POST', body: formData});
        const data = await res.json();
        return data.status === 'success' ? data.url : null;
    }

    showNotification(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed; top: 20px; right: 20px; background: rgba(34,197,94,0.95);
            color: white; padding: 1rem 2rem; border-radius: 12px; z-index: 10000;
            backdrop-filter: blur(10px); font-weight: 500; box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    window.profileApp = new ProfileApp();
});

// Global for inline onclick
function viewAlbum(id) {
    alert(`View album ${id}`);
}

