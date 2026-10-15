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
                    const role = document.querySelector('#user-role');
                    fetchUserRole(data.username).then(roleEl => role.textContent = roleEl.dataset.role || 'Citizen');
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
        // Only event btn opens modal
        const eventBtn = document.getElementById('create-event-btn');
        if (eventBtn) {
            eventBtn.addEventListener('click', () => this.openModal('event-modal'));
        }

        document.querySelectorAll('.modal-close, .glass-modal').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-close') || e.target.classList.contains('glass-modal')) {
                    this.closeModal(e.target.closest('.glass-modal'));
                }
            });
        });

        // Forms
        document.getElementById('post-form').addEventListener('submit', (e) => this.handlePostSubmit(e));
        document.getElementById('album-form').addEventListener('submit', (e) => this.handleAlbumSubmit(e));
        document.getElementById('event-form').addEventListener('submit', (e) => this.handleEventSubmit(e));
        document.getElementById('settings-form').addEventListener('submit', (e) => this.handleSettingsSubmit(e));

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => {
            fetch('/api/logout', {method: 'POST'}).then(() => location.href = '/');
        });

        // Quick actions
        // Only event card opens modal (posts/albums redirect via links)
        const eventCard = document.querySelector('[data-action="event"]');
        if (eventCard) {
            eventCard.addEventListener('click', (e) => {
                this.openModal('event-modal');
            });
        }
    }

    async fetchUserRole(username) {
        const user = await fetchUser(username);
        const roleEl = document.createElement('span');
        roleEl.dataset.role = user.role;
        return roleEl;
    }

    switchSection(section) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

        // Show selected
        document.getElementById(section).classList.add('active');
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Load data
        switch(section) {
            case 'dashboard': this.loadStats(); break;
            case 'posts': this.loadPosts(); break;
            case 'albums': this.loadAlbums(); break;
            case 'events': this.loadEvents(); break;
        }
    }

    loadStats() {
        fetch('/api/profile/stats')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('stat-posts').textContent = data.stats.posts;
                    document.getElementById('stat-albums').textContent = data.stats.albums;
                    document.getElementById('stat-events').textContent = data.stats.events;
                }
            });
    }

    loadPosts() {
        fetch('/api/profile/posts')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    this.renderPosts(data.posts, 'posts-grid');
                }
            });
    }

    renderPosts(posts, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = posts.map(post => `
            <div class="content-card glass-card">
                ${post.image ? `<img src="${post.image}" alt="Cover">` : ''}
                <div class="card-body">
                    <h4>${post.title || 'Untitled'}</h4>
                    <p>${post.content.substring(0, 100)}...</p>
                    <span class="status-badge ${post.status}">${post.status.toUpperCase()}</span>
                    <div class="card-actions">
                        <button class="btn-glass edit-post" data-id="${post.id}">Edit</button>
                        <button class="btn-glass delete-post" data-id="${post.id}">Delete</button>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Bind actions
        container.querySelectorAll('.delete-post').forEach(btn => {
            btn.addEventListener('click', (e) => this.deletePost(e.target.dataset.id));
        });
    }

    loadAlbums() {
        fetch('/api/profile/albums')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    this.renderAlbums(data.albums, 'albums-grid');
                }
            });
    }

    renderAlbums(albums, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = albums.map(album => `
            <div class="content-card glass-card">
                ${album.posts[0]?.image_url ? `<img src="${album.posts[0].image_url}" alt="Album cover">` : ''}
                <div class="card-body">
                    <h4>${album.title}</h4>
                    <p>${album.posts?.length || 0} images</p>
                    <div class="card-actions">
                        <button class="btn-glass" onclick="viewAlbum(${album.id})">View</button>
                        <button class="btn-glass delete-album" data-id="${album.id}">Delete</button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    loadEvents() {
        fetch('/api/profile/events')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    this.renderEvents(data.events, 'events-grid');
                }
            });
    }

    renderEvents(events, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = events.map(event => `
            <div class="content-card glass-card">
                ${event.image ? `<img src="${event.image}" alt="Event">` : ''}
                <div class="card-body">
                    <h4>${event.title}</h4>
                    <p>${new Date(event.date).toLocaleDateString()}</p>
                    <p>${event.location}</p>
                    <div class="card-actions">
                        <button class="btn-glass edit-event" data-id="${event.id}">Edit</button>
                        <button class="btn-glass delete-event" data-id="${event.id}">Delete</button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    openModal(modalId) {
        document.getElementById(modalId).classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    async handlePostSubmit(e) {
        e.preventDefault();
        const formData = {
            title: document.getElementById('post-title').value,
            content: document.getElementById('post-content').value,
            category: document.getElementById('post-category').value,
            status: document.getElementById('post-publish').checked ? 'published' : 'draft'
        };
        
        const imageFile = document.getElementById('post-image').files[0];
        if (imageFile) {
            const imageUrl = await this.uploadFile(imageFile);
            formData.image = imageUrl;
        }

        const res = await fetch('/api/profile/posts', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });

        if (res.ok) {
            this.closeModal(document.getElementById('post-modal'));
            this.loadPosts();
            this.loadStats();
            this.showNotification('Post created successfully!');
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const res = await fetch('/api/upload/image', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        return data.url;
    }

    async deletePost(postId) {
        if (confirm('Delete this post?')) {
            await fetch(`/api/profile/posts/${postId}`, {method: 'DELETE'});
            this.loadPosts();
            this.loadStats();
        }
    }

    async handleAlbumSubmit(e) {
        e.preventDefault();
        // Similar implementation for albums
        alert('Album creation coming soon!');
    }

    async handleEventSubmit(e) {
        e.preventDefault();
        // Similar for events
        alert('Event creation coming soon!');
    }

    async handleSettingsSubmit(e) {
        e.preventDefault();
        const formData = {
            name: document.getElementById('user-name-input').value,
            email: document.getElementById('user-email-input').value
        };
        
        const avatarFile = document.getElementById('avatar-upload').files[0];
        if (avatarFile) {
            formData.avatar = await this.uploadFile(avatarFile);
        }

        await fetch('/api/profile/settings', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        
        this.showNotification('Profile updated!');
        this.loadUserInfo();
    }

    showNotification(message) {
        // Simple toast
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed; top: 20px; right: 20px; background: rgba(34,197,94,0.9);
            color: white; padding: 1rem 2rem; border-radius: 12px; z-index: 10000;
            backdrop-filter: blur(10px); animation: slideInRight 0.3s ease;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

// Utility
async function fetchUser(username) {
    const res = await fetch('/api/check-auth');
    const data = await res.json();
    // Simplified - in real app fetch full user data
    return {username, role: 'citizen'};
}

// Init
document.addEventListener('DOMContentLoaded', () => new ProfileApp());

// Global functions
function viewAlbum(id) {
    alert(`Viewing album ${id}`);
}
