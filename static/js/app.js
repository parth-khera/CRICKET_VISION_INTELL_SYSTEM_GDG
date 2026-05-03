// Chart instances
let wormChart = null, shotChart = null, pressureChart = null, radarChart = null;

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault(); dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', e => { if (e.target.files.length) handleFile(e.target.files[0]); });

    fetchStats();
});

async function handleFile(file) {
    if (!file.type.match('image.*')) { alert('Please upload a JPG or PNG image.'); return; }

    // Immediate local preview
    const reader = new FileReader();
    reader.onload = e => {
        document.getElementById('originalPreview').src = e.target.result;
        document.getElementById('visionSection').style.display = 'block';
        document.getElementById('detectionStatusText').innerText = 'Running Vision Agent...';
    };
    reader.readAsDataURL(file);

    // Status
    const status = document.getElementById('uploadStatus');
    status.innerText = '⚡ Processing with Agents...'; status.style.display = 'block';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/api/analyze', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.status === 'success') {
            updateUI(data);
            status.innerText = '✅ Analysis complete!';
        } else {
            status.innerText = '❌ Error: ' + (data.message || 'Unknown error');
        }
    } catch (err) {
        status.innerText = '❌ Network error. Is the server running?';
    }
}

function updateUI(data) {
    // 1. Vision
    document.getElementById('edgePreview').src = data.vision.edge_map_url;
    document.getElementById('detectionStatusText').innerText =
        `Ball Detection: ${data.vision.detection} | Trajectory: ${data.vision.estimated_trajectory || 'N/A'}`;

    // 2. Event Extraction
    const ev = data.event;
    document.getElementById('eventCard').style.display = 'block';
    document.getElementById('eventGrid').innerHTML = `
        <div class="ev-item"><div class="ev-label">Ball Type</div><div class="ev-val">${ev.ball_type}</div></div>
        <div class="ev-item"><div class="ev-label">Line</div><div class="ev-val">${ev.line}</div></div>
        <div class="ev-item"><div class="ev-label">Shot Played</div><div class="ev-val">${ev.shot}</div></div>
        <div class="ev-item"><div class="ev-label">Runs / Outcome</div><div class="ev-val">${ev.runs} runs</div></div>
    `;

    // 3. Live Context
    const ctx = data.context;
    document.getElementById('contextCard').style.display = 'block';
    document.getElementById('sourceLabel').innerText = ctx.source || 'Simulated';
    if (ctx.live_match_summary) {
        document.getElementById('matchSummaryBox').style.display = 'block';
        document.getElementById('matchSummaryText').innerText = ctx.live_match_summary;
    }
    const phase = ctx.match_phase;
    document.getElementById('contextGrid').innerHTML = `
        <div class="ctx-item"><div class="ctx-label">Phase</div><div class="ctx-val">${phase}</div></div>
        <div class="ctx-item"><div class="ctx-label">Score</div><div class="ctx-val">${ctx.current_score}/${ctx.wickets}</div></div>
        <div class="ctx-item"><div class="ctx-label">Current Over</div><div class="ctx-val">${ctx.current_over}</div></div>
        <div class="ctx-item"><div class="ctx-label">Wickets Down</div><div class="ctx-val">${ctx.wickets}</div></div>
    `;

    // 4. AI Insights
    const ins = data.insights;
    const insightsEl = document.getElementById('insightsContainer');
    insightsEl.innerHTML = '';

    if (ins.error) {
        insightsEl.innerHTML = `<div class="empty-state" style="color:var(--red)">${ins.error}</div>`;
    } else {
        if (ins.visual_analysis)      addInsightCard('Visual Analysis 👁️', ins.visual_analysis, '', '');
        if (ins.tactical_insight)     addInsightCard('Tactical Insight ⚡', ins.tactical_insight, ins.intent, ins.pressure_level);
        if (ins.match_context)        addInsightCard('Match Context 🏟️', ins.match_context, '', '');
        if (ins.next_ball_prediction) addInsightCard('Next Ball Prediction 🔮', ins.next_ball_prediction, '', '');
        if (ins.visual_stats)         renderRadarChart(ins.visual_stats);
        if (ins.api_note || ins.error_note) {
            const note = document.createElement('div');
            note.style.cssText = 'font-size:.78rem;color:var(--muted);margin-top:.3rem;padding:.6rem 1rem;background:rgba(255,255,255,.04);border-radius:7px;border:1px solid rgba(255,255,255,.07);';
            note.innerHTML = `ℹ️ ${ins.api_note || ins.error_note} — <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:var(--cyan);text-decoration:none;font-weight:600;">Get free key ↗</a>`;
            insightsEl.appendChild(note);
        }
    }

    // 5. Stats + Charts
    updateStatsDisplay(data.stats);
    renderCharts(data.stats);
}

function addInsightCard(title, text, intent, pressure) {
    const template = document.getElementById('insightTemplate');
    const clone = template.content.cloneNode(true);
    clone.querySelector('.insight-title').innerText = title;
    clone.querySelector('.insight-desc').innerText = text;

    const badge = clone.querySelector('.insight-badge');
    if (pressure) {
        const p = pressure.toLowerCase();
        badge.innerText = `${pressure} Pressure · ${intent}`;
        badge.classList.add(`badge-${p}`);
    } else { badge.style.display = 'none'; }

    clone.querySelector('.explain-btn').onclick = () => getExplanation(text);
    document.getElementById('insightsContainer').appendChild(clone);
}

function updateStatsDisplay(stats) {
    // Header
    document.getElementById('valProcessed').innerText = stats.total_balls_processed || 0;
    document.getElementById('valAggression').innerText = stats.aggression_index || '0%';
    document.getElementById('valSR').innerText = stats.strike_rate || '0.0';
    document.getElementById('valScore').innerText = `${stats.total_runs || 0}/${stats.wickets || 0}`;

    // Scorecard bar
    document.getElementById('scorecardBar').style.display = 'flex';
    document.getElementById('scRuns').innerText = stats.total_runs || 0;
    document.getElementById('scWickets').innerText = stats.wickets || 0;
    document.getElementById('scBalls').innerText = stats.total_balls_processed || 0;
    document.getElementById('scSR').innerText = stats.strike_rate || '0.0';
    document.getElementById('scAgg').innerText = stats.aggression_index || '0%';
}

function renderCharts(stats) {
    document.getElementById('chartsRow').style.display = 'grid';

    // --- WORM / RUN RATE CHART ---
    const rc = stats.run_rate_chart;
    const wormCtx = document.getElementById('wormChart').getContext('2d');
    if (wormChart) wormChart.destroy();
    if (rc && rc.labels.length > 0) {
        wormChart = new Chart(wormCtx, {
            type: 'line',
            data: {
                labels: rc.labels,
                datasets: [
                    {
                        label: 'Cumulative Runs',
                        data: rc.cumulative,
                        borderColor: 'rgba(0,229,255,1)',
                        backgroundColor: 'rgba(0,229,255,0.1)',
                        tension: 0.4, fill: true,
                        pointRadius: 4, pointHoverRadius: 6,
                        pointBackgroundColor: 'rgba(0,229,255,1)'
                    },
                    {
                        label: 'Runs/Over',
                        data: rc.data,
                        borderColor: 'rgba(255,34,85,1)',
                        backgroundColor: 'transparent',
                        borderDash: [4, 4],
                        tension: 0.4, fill: false,
                        pointRadius: 3
                    }
                ]
            },
            options: chartOptions('Score Progression')
        });
    } else {
        wormCtx.canvas.parentElement.querySelector('h3').innerText = 'Run Rate · Worm (no data yet)';
    }

    // --- SHOT DISTRIBUTION DOUGHNUT ---
    const shotCtx = document.getElementById('shotChart').getContext('2d');
    if (shotChart) shotChart.destroy();
    const shots = stats.shot_distribution || {};
    const shotLabels = Object.keys(shots);
    const shotData = Object.values(shots);
    if (shotLabels.length > 0) {
        shotChart = new Chart(shotCtx, {
            type: 'doughnut',
            data: {
                labels: shotLabels,
                datasets: [{ data: shotData, backgroundColor: donutColors(shotLabels.length), borderWidth: 1 }]
            },
            options: donutOptions()
        });
    }

    // --- PRESSURE DOUGHNUT ---
    const pressCtx = document.getElementById('pressureChart').getContext('2d');
    if (pressureChart) pressureChart.destroy();
    const pd = stats.pressure_distribution || { low: 0, medium: 0, high: 0 };
    pressureChart = new Chart(pressCtx, {
        type: 'doughnut',
        data: {
            labels: ['Low', 'Medium', 'High'],
            datasets: [{ data: [pd.low, pd.medium, pd.high], backgroundColor: ['rgba(0,229,255,.7)', 'rgba(255,200,0,.7)', 'rgba(255,34,85,.7)'], borderWidth: 1 }]
        },
        options: donutOptions()
    });
}

function renderRadarChart(vstats) {
    document.getElementById('radarCard').style.display = 'block';
    const ctx = document.getElementById('visualStatsChart').getContext('2d');
    if (radarChart) radarChart.destroy();
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Aggression', 'Footwork', 'Timing', 'Power'],
            datasets: [{
                label: 'AI Visual Score',
                data: [vstats.Aggression, vstats.Footwork, vstats.Timing_Estimation, vstats.Power],
                backgroundColor: 'rgba(0,229,255,.15)',
                borderColor: 'rgba(0,229,255,1)',
                pointBackgroundColor: 'rgba(255,34,85,1)',
                pointBorderColor: '#fff'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: { color: 'rgba(255,255,255,.1)' },
                    grid: { color: 'rgba(255,255,255,.1)' },
                    pointLabels: { color: '#eaf0fb', font: { family: 'Inter', size: 11 } },
                    ticks: { color: 'rgba(255,255,255,.4)', backdropColor: 'transparent', stepSize: 2 },
                    min: 0, max: 10
                }
            },
            plugins: { legend: { labels: { color: '#eaf0fb', font: { family: 'Outfit' } } } }
        }
    });
}

// Helpers
function chartOptions(title) {
    return {
        responsive: true, maintainAspectRatio: true,
        plugins: { legend: { labels: { color: '#eaf0fb', font: { family: 'Outfit', size: 10 }, boxWidth: 10 } } },
        scales: {
            x: { ticks: { color: '#7a8fa8', font: { size: 9 } }, grid: { color: 'rgba(255,255,255,.05)' } },
            y: { ticks: { color: '#7a8fa8', font: { size: 9 } }, grid: { color: 'rgba(255,255,255,.05)' } }
        }
    };
}

function donutOptions() {
    return {
        responsive: true, maintainAspectRatio: true,
        plugins: {
            legend: { position: 'bottom', labels: { color: '#eaf0fb', font: { family: 'Outfit', size: 10 }, boxWidth: 10, padding: 8 } }
        }
    };
}

function donutColors(n) {
    const palette = ['rgba(0,229,255,.8)', 'rgba(255,34,85,.8)', 'rgba(255,200,0,.8)', 'rgba(0,230,118,.8)', 'rgba(187,134,252,.8)', 'rgba(255,138,101,.8)'];
    return Array.from({ length: n }, (_, i) => palette[i % palette.length]);
}

async function getExplanation(insightText) {
    const expl = document.getElementById('explanationSection');
    const loader = document.getElementById('explLoader');
    const explText = document.getElementById('explText');
    expl.style.display = 'block';
    explText.innerText = '';
    loader.style.display = 'block';
    try {
        const res = await fetch('/api/explain', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ insight: insightText })
        });
        const data = await res.json();
        loader.style.display = 'none';
        explText.innerText = data.explanation;
    } catch {
        loader.style.display = 'none';
        explText.innerText = 'Error fetching explanation.';
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
