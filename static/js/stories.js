// Stories functionality - Instagram-like stories feature

let storiesData = [];
let currentStoryIndex = 0;
let currentUserIndex = 0;
let storyViewerOpen = false;
let storyProgressInterval = null;

// Load stories from API
async function loadStories() {
    try {
        const response = await fetch('/api/stories');
        const data = await response.json();
        
        if (data.success) {
            // Filter out expired stories on frontend as well (double check)
            const now = new Date();
            storiesData = data.stories.map(userStory => {
                return {
                    ...userStory,
                    stories: userStory.stories.filter(story => {
                        if (!story.expires_at) return true;
                        const expiresAt = new Date(story.expires_at);
                        return expiresAt > now;
                    })
                };
            }).filter(userStory => userStory.stories.length > 0); // Remove users with no active stories
            
            renderStoryBar();
        } else {
            console.error('Error loading stories:', data.error);
        }
    } catch (error) {
        console.error('Error fetching stories:', error);
    }
}

// Render story bar at the top
function renderStoryBar() {
    const storyBar = document.getElementById('stories-bar');
    if (!storyBar) return;
    
    // Get current user's email
    const userEmail = sessionStorage.getItem('userEmail');
    
    if (storiesData.length === 0) {
        // If user is logged in, show "Your Story" upload button
        if (userEmail) {
            storyBar.innerHTML = `
                <div class="stories-container">
                    <div class="story-item story-upload story-empty" onclick="openStoryUpload()">
                        <div class="story-avatar upload-avatar empty-avatar">
                            <span class="upload-icon">+</span>
                        </div>
                        <div class="story-username">Your Story</div>
                    </div>
                </div>
            `;
        } else {
            storyBar.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No stories available</p>';
        }
        return;
    }
    
    let html = '<div class="stories-container">';
    
    let userHasStories = false;
    let userStoryIndex = -1;
    
    // First, check if current user has stories (userEmail already defined above)
    storiesData.forEach((userStory, index) => {
        if (userEmail && userStory.user_email === userEmail) {
            userHasStories = true;
            userStoryIndex = index;
        }
    });
    
    // Add "Your Story" button first if user is logged in and doesn't have stories
    if (userEmail && !userHasStories) {
        html += `
            <div class="story-item story-upload story-empty" onclick="openStoryUpload()">
                <div class="story-avatar upload-avatar empty-avatar">
                    <span class="upload-icon">+</span>
                </div>
                <div class="story-username">Your Story</div>
            </div>
        `;
    }
    
    // Render all stories
    storiesData.forEach((userStory, index) => {
        const firstStory = userStory.stories[0];
        const storyUrl = `/uploads/stories/${firstStory.filename}`;
        const hasNewStories = checkIfNewStories(userStory);
        const isCurrentUser = userStory.user_email === userEmail;
        
        const userInitial = userStory.user_name.charAt(0).toUpperCase();
        html += `
            <div class="story-item ${hasNewStories ? 'has-new' : ''} ${isCurrentUser ? 'your-story' : ''}" onclick="openStoryViewer(${index})">
                <div class="story-avatar" data-initial="${userInitial}">
                    ${userStory.stories.length > 1 ? '<span class="story-count">' + userStory.stories.length + '</span>' : ''}
                </div>
                <div class="story-username">${isCurrentUser ? 'Your Story' : userStory.user_name}</div>
            </div>
        `;
    });
    
    html += '</div>';
    storyBar.innerHTML = html;
}

function checkIfNewStories(userStory) {
    // Check if any story is less than 1 hour old
    const now = new Date();
    for (let story of userStory.stories) {
        const createdAt = new Date(story.created_at);
        const hoursDiff = (now - createdAt) / (1000 * 60 * 60);
        if (hoursDiff < 1) {
            return true;
        }
    }
    return false;
}

// Open story viewer
function openStoryViewer(userIndex) {
    if (userIndex < 0 || userIndex >= storiesData.length) return;
    
    currentUserIndex = userIndex;
    currentStoryIndex = 0;
    storyViewerOpen = true;
    
    const viewer = document.getElementById('story-viewer');
    if (viewer) {
        viewer.style.display = 'flex';
        showCurrentStory();
        startStoryProgress();
    }
}

// Show current story
function showCurrentStory() {
    const viewer = document.getElementById('story-viewer');
    if (!viewer) return;
    
    const userStory = storiesData[currentUserIndex];
    if (!userStory || currentStoryIndex >= userStory.stories.length) {
        // Move to next user
        if (currentUserIndex < storiesData.length - 1) {
            currentUserIndex++;
            currentStoryIndex = 0;
            showCurrentStory();
        } else {
            closeStoryViewer();
        }
        return;
    }
    
    const story = userStory.stories[currentStoryIndex];
    const storyUrl = `/uploads/stories/${story.filename}`;
    
    const mediaHtml = story.media_type === 'video' 
        ? `<video src="${storyUrl}" autoplay muted loop playsinline class="story-media"></video>`
        : `<img src="${storyUrl}" alt="Story" class="story-media">`;
    
    const timeAgo = getTimeAgo(story.created_at);
    
    viewer.innerHTML = `
        <div class="story-viewer-content">
            <div class="story-progress-container">
                ${userStory.stories.map((_, idx) => `
                    <div class="story-progress-bar">
                        <div class="story-progress-fill" data-story-index="${idx}"></div>
                    </div>
                `).join('')}
            </div>
            
            <div class="story-header">
                <div class="story-user-info">
                    <div class="story-user-avatar">${userStory.user_name.charAt(0).toUpperCase()}</div>
                    <div>
                        <div class="story-user-name">${userStory.user_name}</div>
                        <div class="story-time">${timeAgo}</div>
                    </div>
                </div>
                <button class="story-close-btn" onclick="closeStoryViewer()">×</button>
            </div>
            
            <div class="story-media-container">
                ${mediaHtml}
            </div>
            
            <div class="story-nav">
                <button class="story-nav-btn story-prev" onclick="previousStory()">‹</button>
                <button class="story-nav-btn story-next" onclick="nextStory()">›</button>
            </div>
        </div>
    `;
    
    // Reset progress
    resetStoryProgress();
}

function getTimeAgo(dateString) {
    // Parse the ISO date string and convert to local time
    const storyDate = new Date(dateString);
    const now = new Date();
    
    // Calculate difference in milliseconds
    const diffMs = now.getTime() - storyDate.getTime();
    
    // Convert to different time units
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    // Return appropriate time string
    if (diffSecs < 60) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return '1d ago';
    return `${diffDays}d ago`;
}

// Story navigation
function nextStory() {
    const userStory = storiesData[currentUserIndex];
    if (currentStoryIndex < userStory.stories.length - 1) {
        currentStoryIndex++;
    } else if (currentUserIndex < storiesData.length - 1) {
        currentUserIndex++;
        currentStoryIndex = 0;
    } else {
        closeStoryViewer();
        return;
    }
    showCurrentStory();
    startStoryProgress();
}

function previousStory() {
    if (currentStoryIndex > 0) {
        currentStoryIndex--;
    } else if (currentUserIndex > 0) {
        currentUserIndex--;
        const userStory = storiesData[currentUserIndex];
        currentStoryIndex = userStory.stories.length - 1;
    }
    showCurrentStory();
    startStoryProgress();
}

// Story progress
function startStoryProgress() {
    stopStoryProgress();
    
    const progressBar = document.querySelector(`.story-progress-fill[data-story-index="${currentStoryIndex}"]`);
    if (!progressBar) return;
    
    progressBar.style.transition = 'width 5s linear';
    progressBar.style.width = '100%';
    
    storyProgressInterval = setTimeout(() => {
        nextStory();
    }, 5000);
}

function stopStoryProgress() {
    if (storyProgressInterval) {
        clearTimeout(storyProgressInterval);
        storyProgressInterval = null;
    }
    
    document.querySelectorAll('.story-progress-fill').forEach(bar => {
        bar.style.transition = 'none';
        bar.style.width = '0%';
    });
}

function resetStoryProgress() {
    stopStoryProgress();
    document.querySelectorAll('.story-progress-fill').forEach((bar, idx) => {
        if (idx < currentStoryIndex) {
            bar.style.width = '100%';
        } else {
            bar.style.width = '0%';
        }
    });
}

function closeStoryViewer() {
    stopStoryProgress();
    storyViewerOpen = false;
    const viewer = document.getElementById('story-viewer');
    if (viewer) {
        viewer.style.display = 'none';
    }
}

// Story upload
function openStoryUpload() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,video/*';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // Check file size (50MB max)
        if (file.size > 50 * 1024 * 1024) {
            alert('File size too large. Maximum size is 50MB.');
            return;
        }
        
        await uploadStory(file);
    };
    input.click();
}

async function uploadStory(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/stories/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Story uploaded successfully! It will be visible for 24 hours.');
            loadStories(); // Reload stories
        } else {
            alert('Error uploading story: ' + data.error);
        }
    } catch (error) {
        console.error('Error uploading story:', error);
        alert('Error uploading story. Please try again.');
    }
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (!storyViewerOpen) return;
    
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        nextStory();
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        previousStory();
    } else if (e.key === 'Escape') {
        closeStoryViewer();
    }
});

// Load stories on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadStories);
} else {
    loadStories();
}

// Refresh stories every 5 minutes
setInterval(loadStories, 5 * 60 * 1000);

