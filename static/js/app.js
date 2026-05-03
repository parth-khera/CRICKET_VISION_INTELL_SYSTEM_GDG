document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    // Drag and drop setup
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    // Fetch initial stats
    fetchStats();
});

async function handleFile(file) {
    if (!file.type.match('image.*')) {
        alert('Please upload an image file (JPG/PNG).');
        return;
    }

    // Show preview immediately locally
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('originalPreview').src = e.target.result;
        document.getElementById('visionSection').style.display = 'block';
        document.getElementById('detectionStatusText').innerText = "Analyzing visual data...";
    };
    reader.readAsDataURL(file);

    // Show uploading state
    const uploadZone = document.getElementById('dropZone');
    const overlay = document.createElement('div');
    overlay.className = 'uploading-overlay';
    overlay.innerHTML = '<div class="spinner"></div><p>Processing with Agents...</p>';
    uploadZone.style.position = 'relative';
    uploadZone.appendChild(overlay);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            updateUI(data);
        } else {
            alert('Error processing image: ' + data.message);
        }
    } catch (err) {
        console.error(err);
        alert('Network error while communicating with intelligence pipeline.');
    } finally {
        uploadZone.removeChild(overlay);
    }
}

function updateUI(data) {
    // 1. Vision Agent
    document.getElementById('edgePreview').src = data.vision.edge_map_url;
    document.getElementById('detectionStatusText').innerText = `Vision successful. Ball detection: ${data.vision.detection}`;
    
    // 2. Structuring Agent (Event)
    const eventGrid = document.getElementById('eventGrid');
    eventGrid.innerHTML = `
        <div class="data-item"><span class="data-label">Ball Type</span><span class="data-value">${data.event.ball_type}</span></div>
        <div class="data-item"><span class="data-label">Line</span><span class="data-value">${data.event.line}</span></div>
        <div class="data-item"><span class="data-label">Shot</span><span class="data-value">${data.event.shot}</span></div>
        <div class="data-item"><span class="data-label">Runs/Outcome</span><span class="data-value">${data.event.runs}</span></div>
    `;

    // 3. Context Agent
    const contextGrid = document.getElementById('contextGrid');
    let summaryHtml = '';
    if (data.context.live_match_summary) {
        summaryHtml = `<div class="data-item" style="grid-column: 1 / -1;"><span class="data-label" style="color: var(--accent-secondary);">Live Internet Data</span><span class="data-value" style="font-size: 0.9rem;">${data.context.live_match_summary}</span></div>`;
    }
    
    contextGrid.innerHTML = `
        ${summaryHtml}
        <div class="data-item"><span class="data-label">Phase</span><span class="data-value">${data.context.match_phase}</span></div>
        <div class="data-item"><span class="data-label">Score</span><span class="data-value">${data.context.current_score}/${data.context.wickets} (Ov ${data.context.current_over})</span></div>
        <div class="data-item" style="grid-column: 1 / -1;"><span class="data-label">Source</span><span class="data-value" style="font-size: 0.8rem; color: var(--text-muted);">${data.context.source}</span></div>
    `;

    // 4. Intelligence Agent
    const insightsContainer = document.getElementById('insightsContainer');
    insightsContainer.innerHTML = ''; // clear

    const iData = data.insights;
    if (iData.error) {
        insightsContainer.innerHTML = `<div class="empty-state" style="color:var(--accent-secondary)">${iData.error}</div>`;
        return;
    }

    // Create tactical insight card
    addInsightCard('Tactical Insight', iData.tactical_insight, iData.intent, iData.pressure_level);
    
    // Create match context card
    addInsightCard('Match Understanding', iData.match_context, '', '');

    // Create Next Ball Prediction card!
    if (iData.next_ball_prediction) {
        addInsightCard('Next Ball Prediction 🔮', iData.next_ball_prediction, '', '');
    }

    // 5. Update Stats
    updateStatsDisplay(data.stats);
}

function addInsightCard(title, text, intent, pressure) {
    const template = document.getElementById('insightTemplate');
    const clone = template.content.cloneNode(true);
    
    const item = clone.querySelector('.insight-item');
    item.classList.add('fade-in');
    
    clone.querySelector('.insight-title').innerText = title;
    clone.querySelector('.insight-desc').innerText = text;
    
    const badge = clone.querySelector('.insight-badge');
    if (pressure) {
        badge.innerText = `Pressure: ${pressure} | Intent: ${intent}`;
        if (pressure.toLowerCase() === 'high') badge.classList.add('badge-high');
        else if (pressure.toLowerCase() === 'medium') badge.classList.add('badge-medium');
        else badge.classList.add('badge-low');
    } else {
        badge.style.display = 'none';
    }

    const btn = clone.querySelector('.explain-btn');
    btn.onclick = () => getExplanation(text);

    document.getElementById('insightsContainer').appendChild(clone);
}

async function getExplanation(insightText) {
    const explSection = document.getElementById('explanationSection');
    const explText = document.getElementById('explText');
    const loader = document.getElementById('explLoader');
    
    explSection.style.display = 'block';
    explText.innerText = '';
    loader.style.display = 'block';

    try {
        const response = await fetch('/api/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ insight: insightText })
        });
        
        const data = await response.json();
        loader.style.display = 'none';
        explText.innerText = data.explanation;
    } catch (err) {
        loader.style.display = 'none';
        explText.innerText = "Error fetching explanation.";
    }
}

function hideExplanation() {
    document.getElementById('explanationSection').style.display = 'none';
}

async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        updateStatsDisplay(data);
    } catch(e) {}
}

function updateStatsDisplay(stats) {
    document.getElementById('valProcessed').innerText = stats.total_balls_processed || 0;
    document.getElementById('valAggression').innerText = stats.aggression_index || '0%';
}
