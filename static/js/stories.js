// Stories functionality - Instagram-like stories feature

let storiesData = [];
let currentStoryIndex = 0;
let currentUserIndex = 0;
let storyViewerOpen = false;
let storyProgressInterval = null;

// Load stories from API
async function loadStories() {
    try {
        console.log('Loading stories from API...');
        const response = await fetch('/api/stories');
        const data = await response.json();
        
        console.log('Stories API response:', data);
        
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
            
            console.log('Filtered stories data:', storiesData);
        } else {
            console.error('Error loading stories:', data.error);
            storiesData = []; // Set to empty array on error
        }
    } catch (error) {
        console.error('Error fetching stories:', error);
        storiesData = []; // Set to empty array on error
    }
    
    // Always render the bar, even if there are no stories
    renderStoryBar();
}

// Render story bar at the top
function renderStoryBar() {
    const storyBar = document.getElementById('stories-bar');
    if (!storyBar) {
        console.warn('Stories bar element not found');
        return;
    }
    
    // Get current user's email from data attribute or sessionStorage
    let userEmail = storyBar.getAttribute('data-user-email');
    if (!userEmail || userEmail === '' || userEmail === 'None') {
        userEmail = sessionStorage.getItem('userEmail');
    }
    let userName = storyBar.getAttribute('data-user-name');
    if (!userName || userName === 'User' || userName === '' || userName === 'None') {
        userName = sessionStorage.getItem('userName') || (userEmail ? userEmail.split('@')[0] : 'User');
    }
    
    console.log('🎨 Rendering story bar');
    console.log('   - userEmail:', userEmail);
    console.log('   - userName:', userName);
    console.log('   - storiesData length:', storiesData.length);
    console.log('   - storyBar element:', storyBar);
    console.log('   - data-user-email:', storyBar.getAttribute('data-user-email'));
    console.log('   - data-user-name:', storyBar.getAttribute('data-user-name'));
    
    // Always show upload button for logged-in users (check for valid email)
    const shouldShowUpload = userEmail && 
                             userEmail !== 'Guest' && 
                             userEmail !== '' && 
                             userEmail !== 'user@example.com' &&
                             userEmail !== 'None' &&
                             userEmail.includes('@'); // Must be a valid email format
    
    console.log('   - shouldShowUpload:', shouldShowUpload);
    
    // If no stories, always show upload button for logged-in users
    if (storiesData.length === 0) {
        if (shouldShowUpload) {
            storyBar.innerHTML = `
                <div class="stories-container">
                    <div class="story-item story-upload story-empty" onclick="if(typeof openStoryUpload === 'function') { openStoryUpload(); } else { console.error(\'openStoryUpload not defined\'); }" style="cursor: pointer;">
                        <div class="story-avatar upload-avatar empty-avatar">
                            <span class="upload-icon" style="font-size: 24px; color: #262626; line-height: 60px; display: block;">+</span>
                        </div>
                        <div class="story-username">Your Story</div>
                    </div>
                </div>
            `;
            console.log('✅ Rendered upload button for logged-in user (no stories)');
            console.log('   - Upload button HTML inserted');
            storyBar.style.display = 'block';
            storyBar.style.visibility = 'visible';
            storyBar.style.opacity = '1';
            storyBar.style.minHeight = '120px';
        } else {
            storyBar.innerHTML = '<p style="text-align: center; color: #666; padding: 20px; margin: 0;">No stories available. <a href="/login-page" style="color: #4CAF50; text-decoration: underline;">Login</a> to upload your story.</p>';
            console.log('⚠️ No user email, showing login message');
            console.log('   - userEmail was:', userEmail);
            storyBar.style.display = 'block';
            storyBar.style.visibility = 'visible';
            storyBar.style.opacity = '1';
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
    if (userEmail && userEmail !== 'Guest' && userEmail !== '' && !userHasStories) {
        html += `
            <div class="story-item story-upload story-empty" onclick="openStoryUpload()" style="cursor: pointer;">
                <div class="story-avatar upload-avatar empty-avatar">
                    <span class="upload-icon" style="font-size: 24px; color: #262626;">+</span>
                </div>
                <div class="story-username">Your Story</div>
            </div>
        `;
        console.log('Added upload button for user without stories');
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
    storyBar.style.display = 'block';
    storyBar.style.visibility = 'visible';
    console.log('Story bar rendered with', storiesData.length, 'users and upload button:', shouldShowUpload && !userHasStories);
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
function initStories() {
    console.log('🚀 Initializing stories...');
    console.log('Document ready state:', document.readyState);
    const storyBar = document.getElementById('stories-bar');
    if (storyBar) {
        console.log('✅ Stories bar found:', storyBar);
        let userEmail = storyBar.getAttribute('data-user-email');
        let userName = storyBar.getAttribute('data-user-name');
        
        // Fallback to sessionStorage if data attributes are empty
        if (!userEmail || userEmail === '') {
            userEmail = sessionStorage.getItem('userEmail');
        }
        if (!userName || userName === 'User' || userName === '') {
            userName = sessionStorage.getItem('userName') || userEmail?.split('@')[0] || 'User';
        }
        
        console.log('📧 Stories bar data attributes:', {
            email: userEmail,
            name: userName,
            dataEmail: storyBar.getAttribute('data-user-email'),
            dataName: storyBar.getAttribute('data-user-name')
        });
        console.log('📦 SessionStorage userEmail:', sessionStorage.getItem('userEmail'));
        
        // Make sure bar is visible
        storyBar.style.display = 'block';
        storyBar.style.visibility = 'visible';
        storyBar.style.opacity = '1';
        storyBar.setAttribute('data-user-email', userEmail || '');
        storyBar.setAttribute('data-user-name', userName || 'User');
        
        // Load stories immediately
        loadStories();
    } else {
        console.warn('⚠️ Stories bar not found, retrying in 100ms...');
        setTimeout(initStories, 100);
    }
}

// Try multiple initialization methods
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStories);
} else {
    // DOM already loaded, initialize immediately
    initStories();
}

// Also try after a short delay to ensure everything is loaded
setTimeout(() => {
    const storyBar = document.getElementById('stories-bar');
    if (storyBar) {
        const userEmail = storyBar.getAttribute('data-user-email') || sessionStorage.getItem('userEmail');
        const isEmpty = storyBar.innerHTML.trim() === '';
        
        console.log('🔍 Delayed check - Stories bar empty:', isEmpty, 'User email:', userEmail);
        
        if (isEmpty) {
            console.log('🔄 Stories bar is empty, re-initializing...');
            // Force visibility
            storyBar.style.display = 'block';
            storyBar.style.visibility = 'visible';
            storyBar.style.opacity = '1';
            initStories();
        }
    } else {
        console.warn('⚠️ Stories bar still not found after delay');
    }
}, 1000);

// Refresh stories every 5 minutes
setInterval(loadStories, 5 * 60 * 1000);

