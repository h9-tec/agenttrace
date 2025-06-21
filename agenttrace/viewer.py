import json
import sqlite3
import webbrowser
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from .db import _DEFAULT_PATH

app = FastAPI()


def get_runs(db_path: Path = _DEFAULT_PATH) -> List[Dict[str, Any]]:
    """Get all runs from the database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    runs = []
    for row in conn.execute("SELECT * FROM runs ORDER BY start_ts DESC"):
        runs.append(dict(row))
    
    conn.close()
    return runs


def get_steps(run_id: int, db_path: Path = _DEFAULT_PATH) -> List[Dict[str, Any]]:
    """Get all steps for a specific run."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    steps = []
    for row in conn.execute("SELECT * FROM steps WHERE run_id = ? ORDER BY ts", (run_id,)):
        step_dict = dict(row)
        # Parse JSON payload
        try:
            step_dict['payload'] = json.loads(step_dict['payload'])
        except:
            pass
        steps.append(step_dict)
    
    conn.close()
    return steps


@app.get("/")
async def index():
    """Serve the main viewer page."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>AgentTrace Viewer</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
        .runs-list {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        .run-item {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .run-item:hover {
            background: #f8f8f8;
            border-color: #2196F3;
        }
        .run-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .run-name {
            font-weight: 600;
            color: #2196F3;
        }
        .run-meta {
            font-size: 0.9em;
            color: #666;
        }
        .timeline {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            display: none;
        }
        .timeline.active {
            display: block;
        }
        .timeline-header {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }
        .step {
            position: relative;
            padding: 10px 20px;
            border-left: 3px solid #e0e0e0;
            margin-left: 20px;
        }
        .step::before {
            content: '';
            position: absolute;
            left: -8px;
            top: 15px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #fff;
            border: 3px solid #2196F3;
        }
        .step.llm_start { border-left-color: #4CAF50; }
        .step.llm_start::before { border-color: #4CAF50; }
        
        .step.llm_end { border-left-color: #4CAF50; }
        .step.llm_end::before { border-color: #4CAF50; }
        
        .step.tool_start { border-left-color: #FF9800; }
        .step.tool_start::before { border-color: #FF9800; }
        
        .step.tool_end { border-left-color: #FF9800; }
        .step.tool_end::before { border-color: #FF9800; }
        
        .step.chain_start { border-left-color: #9C27B0; }
        .step.chain_start::before { border-color: #9C27B0; }
        
        .step.chain_end { border-left-color: #9C27B0; }
        .step.chain_end::before { border-color: #9C27B0; }
        
        .step.error { border-left-color: #F44336; }
        .step.error::before { border-color: #F44336; }
        
        .step-type {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .step-time {
            font-size: 0.8em;
            color: #999;
            margin-bottom: 5px;
        }
        .step-details {
            font-size: 0.9em;
            color: #666;
            background: #f5f5f5;
            padding: 8px;
            border-radius: 4px;
            margin-top: 5px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error-msg {
            background: #ffebee;
            color: #c62828;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 AgentTrace Viewer</h1>
        
        <div class="runs-list" id="runsList">
            <div class="loading">Loading runs...</div>
        </div>
        
        <div class="timeline" id="timeline">
            <div class="timeline-header" id="timelineHeader"></div>
            <div id="timelineContent"></div>
        </div>
    </div>

    <script>
        let currentRun = null;

        async function loadRuns() {
            try {
                const response = await fetch('/api/runs');
                const runs = await response.json();
                
                const runsList = document.getElementById('runsList');
                
                if (runs.length === 0) {
                    runsList.innerHTML = '<div class="error-msg">No runs found. Start tracing some functions!</div>';
                    return;
                }
                
                runsList.innerHTML = runs.map(run => `
                    <div class="run-item" onclick="loadTimeline(${run.id})">
                        <div class="run-header">
                            <div class="run-name">${run.func_name}</div>
                            <div class="run-meta">
                                <span>Git: ${run.git_sha}</span> | 
                                <span>${formatTime(run.start_ts)}</span>
                                ${run.end_ts ? ` | Duration: ${getDuration(run.start_ts, run.end_ts)}` : ' | Running...'}
                            </div>
                        </div>
                    </div>
                `).join('');
                
                // Auto-load first run
                if (runs.length > 0) {
                    loadTimeline(runs[0].id);
                }
            } catch (error) {
                document.getElementById('runsList').innerHTML = 
                    '<div class="error-msg">Error loading runs: ' + error.message + '</div>';
            }
        }

        async function loadTimeline(runId) {
            currentRun = runId;
            
            try {
                const response = await fetch(`/api/runs/${runId}/steps`);
                const steps = await response.json();
                
                const timeline = document.getElementById('timeline');
                const header = document.getElementById('timelineHeader');
                const content = document.getElementById('timelineContent');
                
                timeline.classList.add('active');
                header.textContent = `Timeline for Run #${runId}`;
                
                if (steps.length === 0) {
                    content.innerHTML = '<div class="error-msg">No steps recorded for this run.</div>';
                    return;
                }
                
                content.innerHTML = steps.map(step => {
                    const stepClass = step.kind.includes('error') ? 'error' : step.kind;
                    const details = typeof step.payload === 'object' ? 
                        JSON.stringify(step.payload, null, 2) : step.payload;
                    
                    return `
                        <div class="step ${stepClass}">
                            <div class="step-type">${formatStepType(step.kind)}</div>
                            <div class="step-time">${formatTime(step.ts)}</div>
                            ${details ? `<div class="step-details">${details}</div>` : ''}
                        </div>
                    `;
                }).join('');
            } catch (error) {
                document.getElementById('timelineContent').innerHTML = 
                    '<div class="error-msg">Error loading timeline: ' + error.message + '</div>';
            }
        }

        function formatTime(isoString) {
            const date = new Date(isoString);
            return date.toLocaleTimeString() + '.' + date.getMilliseconds();
        }

        function getDuration(start, end) {
            const duration = new Date(end) - new Date(start);
            if (duration < 1000) return duration + 'ms';
            if (duration < 60000) return (duration / 1000).toFixed(1) + 's';
            return Math.floor(duration / 60000) + 'm ' + ((duration % 60000) / 1000).toFixed(1) + 's';
        }

        function formatStepType(type) {
            return type.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }

        // Load runs on page load
        loadRuns();
        
        // Auto-refresh every 2 seconds
        setInterval(loadRuns, 2000);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/api/runs")
async def api_runs():
    """API endpoint to get all runs."""
    try:
        return get_runs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/runs/{run_id}/steps")
async def api_steps(run_id: int):
    """API endpoint to get steps for a specific run."""
    try:
        return get_steps(run_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_viewer(port: int = 8000, open_browser: bool = True):
    """Start the viewer web server."""
    if open_browser:
        webbrowser.open(f"http://localhost:{port}")
    
    uvicorn.run(app, host="localhost", port=port, log_level="error") 