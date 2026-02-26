"""
Web-based UI for C-BOM (Cryptographic Bill of Materials) using Flask
"""

import json
import os
import tempfile
import webbrowser
from typing import Optional
from .models import CryptoAsset, CryptoBOM
from .validator import CryptoBOMValidator


def create_app(bom: Optional[CryptoBOM] = None):
    """
    Create and return the Flask application (WSGI factory).
    Use this for production: gunicorn wsgi:app
    """
    try:
        from flask import Flask, render_template_string, request, jsonify, send_file
    except ImportError:
        raise ImportError("Flask not installed. Install with: pip install flask")

    app = Flask(__name__)
    app.json.ensure_ascii = True  # prevent surrogate/non-ASCII encode errors

    # Initialize BOM if none provided
    if bom is None:
        bom = CryptoBOM("C-BOM Web Project", "Cryptographic Asset Inventory")

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>C-BOM - Cryptographic Bill of Materials</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f5f5;
                color: #333;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header h1 { font-size: 2em; margin-bottom: 5px; }
            .header p { font-size: 0.9em; opacity: 0.9; }
            
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            
            .nav { 
                background: white;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            
            .nav button {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9em;
                transition: background 0.3s;
            }
            
            .nav button:hover { background: #764ba2; }
            .nav button.active { background: #764ba2; }
            
            .section { display: none; }
            .section.active { display: block; }
            
            .card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            
            .summary-box {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
            
            .summary-box .number { font-size: 2em; font-weight: bold; }
            .summary-box .label { font-size: 0.8em; margin-top: 5px; opacity: 0.9; }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            
            th {
                background: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }
            
            td {
                padding: 12px;
                border-bottom: 1px solid #ecf0f1;
            }
            
            tr:hover { background: #f5f5f5; }
            
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: 600; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            
            button.primary {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
            }
            button.primary:hover { background: #764ba2; }
            
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: 600;
                background: #667eea;
                color: white;
            }
            .badge-CRITICAL { background: #dc3545 !important; }
            .badge-HIGH     { background: #fd7e14 !important; }
            .badge-MEDIUM   { background: #ffc107 !important; color: #333 !important; }
            .badge-LOW      { background: #28a745 !important; }

            .algo-warning {
                display: none;
                padding: 10px 14px;
                border-radius: 4px;
                margin-top: 6px;
                font-size: 0.9em;
                border-left: 4px solid;
            }
            .chart-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 20px 0;
            }
            .chart-box {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .chart-box h3 { margin-bottom: 15px; color: #555; }
            .add-feedback {
                display: none;
                padding: 12px 16px;
                border-radius: 4px;
                margin-top: 15px;
                font-weight: 600;
            }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    </head>
    <body>
        <div class="header">
            <h1>🔐 C-BOM</h1>
            <p>Cryptographic Bill of Materials</p>
        </div>
        
        <div class="container">
            <div class="nav">
                <button class="nav-btn active" onclick="showSection('dashboard')">📊 Dashboard</button>
                <button class="nav-btn" onclick="showSection('assets')">🔑 Assets</button>
                <button class="nav-btn" onclick="showSection('add-asset')">➕ Add</button>
                <button class="nav-btn" onclick="showSection('validate')">✓ Validate</button>
                <button class="nav-btn" onclick="showSection('export')">💾 Export</button>
            </div>
            
            <div id="dashboard" class="section active">
                <h2>Security Dashboard</h2>
                <div id="summary" class="summary-grid"></div>
                <div class="chart-grid">
                    <div class="chart-box">
                        <h3>Risk Distribution</h3>
                        <canvas id="riskChart" height="220"></canvas>
                    </div>
                    <div class="chart-box">
                        <h3>Asset Types</h3>
                        <canvas id="typeChart" height="220"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h3>Audit Log</h3>
                    <div id="audit-log"></div>
                </div>
            </div>
            
            <div id="assets" class="section">
                <h2>Cryptographic Assets</h2>
                <div class="card">
                    <table>
                        <thead><tr>
                            <th>ID</th><th>Name</th><th>Type</th><th>Algorithm</th><th>Risk</th><th>Status</th><th>Actions</th>
                        </tr></thead>
                        <tbody id="assetsBody"></tbody>
                    </table>
                </div>
            </div>
            
            <div id="add-asset" class="section">
                <h2>Add Asset</h2>

                <div class="card" style="margin-bottom:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;cursor:pointer;" onclick="toggleScanPanel()">
                        <strong>🌐 Read assets from a website</strong>
                        <span id="scanPanelArrow" style="font-size:0.85em;color:#667eea;">&#9660; expand</span>
                    </div>
                    <div id="scanPanel" style="display:none;margin-top:14px;">
                        <p style="color:#666;font-size:0.9em;margin-bottom:10px;">Enter a hostname — the scanner will read its TLS version and certificate and pre-fill two assets below.</p>
                        <div style="display:flex;gap:10px;align-items:flex-end;">
                            <div style="flex:1;">
                                <label>Hostname or URL</label>
                                <input type="text" id="wsUrl" placeholder="e.g. github.com or https://example.com" onkeydown="if(event.key==='Enter'){event.preventDefault();scanWebsite();}">
                            </div>
                            <button type="button" class="primary" id="wsScanBtn" onclick="scanWebsite()" style="height:42px;min-width:90px;">Scan</button>
                        </div>
                        <div id="wsScanSpinner" style="display:none;margin-top:10px;color:#667eea;font-size:0.9em;">&#9203; Scanning&hellip;</div>
                        <div id="wsScanError" style="display:none;margin-top:10px;padding:10px 14px;border-radius:4px;border-left:4px solid #dc3545;background:#f8d7da;color:#721c24;font-size:0.9em;"></div>
                        <div id="wsScanAssets" style="display:none;margin-top:14px;"></div>
                    </div>
                </div>

                <div class="card">
                    <form onsubmit="addAsset(event)">
                        <div class="form-group">
                            <label>Asset ID *</label>
                            <input type="text" id="assetId" required>
                        </div>
                        <div class="form-group">
                            <label>Name *</label>
                            <input type="text" id="assetName" required>
                        </div>
                        <div class="form-group">
                            <label>Type *</label>
                            <select id="assetType" required>
                                <option value="">Select</option>
                                <option value="algorithm">Algorithm</option>
                                <option value="key">Key</option>
                                <option value="certificate">Certificate</option>
                                <option value="library">Library</option>
                                <option value="cipher_suite">Cipher Suite</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Algorithm *</label>
                            <input type="text" id="algorithm" required oninput="checkAlgorithm()">
                            <div id="algoWarning" class="algo-warning"></div>
                        </div>
                        <div class="form-group">
                            <label>Key Length <span style="color:#999;font-weight:normal;">(bits)</span></label>
                            <input type="number" id="keyLength" oninput="checkKeyLength()" onblur="checkKeyLength()" placeholder="e.g. 256">
                            <div id="keyLengthWarning" style="display:none;margin-top:6px;font-size:0.9em;padding:8px 12px;border-radius:4px;border-left:4px solid #ffc107;background:#fff3cd;color:#856404;">
                                ⚠️ Key length is recommended — without it, validation may flag this asset.
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Status</label>
                            <select id="status">
                                <option value="active">Active</option>
                                <option value="deprecated">Deprecated</option>
                                <option value="vulnerable">Vulnerable</option>
                            </select>
                        </div>
                        <button type="submit" class="primary">Add Asset</button>
                        <div id="addFeedback" class="add-feedback"></div>
                    </form>
                </div>
            </div>
            
            <div id="validate" class="section">
                <h2>Validate BOM</h2>
                <div class="card">
                    <button class="primary" onclick="validateBOM()">▶ Run Validation</button>
                    <div id="validationResult" style="margin-top:20px;"></div>
                    <div id="validationChartWrap" style="display:none;margin-top:30px;">
                        <div style="display:grid;grid-template-columns:280px 1fr;gap:30px;align-items:start;">
                            <div>
                                <h3 style="margin-bottom:12px;color:#555;">Results Overview</h3>
                                <canvas id="validationChart" height="240"></canvas>
                            </div>
                            <div>
                                <h3 style="margin-bottom:12px;color:#555;">Per-Asset Report</h3>
                                <div id="assetValidationTable"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="export" class="section">
                <h2>Export</h2>
                <div class="card">
                    <button class="primary" onclick="exportJSON()" style="margin-right: 10px;">JSON</button>
                    <button class="primary" onclick="exportCSV()">CSV</button>
                </div>
            </div>
        </div>
        
        <script>
            let riskChartInst = null, typeChartInst = null;
            const WEAK_ALGOS = ['MD5','SHA-1','SHA1','DES','3DES','RC4','RC2','RC5','SSLv2','SSLv3','NULL','EXPORT'];

            function showSection(id) {
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                document.getElementById(id).classList.add('active');
                if (id === 'dashboard') loadDashboard();
                else if (id === 'assets') loadAssets();
            }

            function riskBadge(risk) {
                return `<span class="badge badge-${risk}">${risk}</span>`;
            }

            function loadDashboard() {
                fetch('/api/summary').then(r => r.json()).then(data => {
                    const scoreColor = data.security_score >= 80
                        ? 'linear-gradient(135deg,#28a745,#20c997)'
                        : data.security_score >= 60
                        ? 'linear-gradient(135deg,#ffc107,#fd7e14)'
                        : 'linear-gradient(135deg,#dc3545,#c82333)';
                    document.getElementById('summary').innerHTML = `
                        <div class="summary-box">
                            <div class="number">${data.total_assets}</div>
                            <div class="label">Total Assets</div>
                        </div>
                        <div class="summary-box" style="background:${scoreColor}">
                            <div class="number">${data.security_score}/100</div>
                            <div class="label">Security Score</div>
                        </div>
                        <div class="summary-box" style="background:linear-gradient(135deg,#dc3545,#c82333)">
                            <div class="number">${data.critical_risk}</div>
                            <div class="label">Critical Risk</div>
                        </div>
                        <div class="summary-box" style="background:linear-gradient(135deg,#fd7e14,#e8590c)">
                            <div class="number">${data.vulnerable_assets}</div>
                            <div class="label">Vulnerable</div>
                        </div>`;
                });
                fetch('/api/chart-data').then(r => r.json()).then(data => {
                    renderRiskChart(data.risk_levels);
                    renderTypeChart(data.asset_types);
                });
                fetch('/api/audit-log').then(r => r.json()).then(logs => {
                    let html = '<ul style="list-style:none;">';
                    if (!logs.length) html += '<li style="padding:10px;color:#999;">No activity yet.</li>';
                    logs.forEach(log => {
                        html += `<li style="padding:10px;border-bottom:1px solid #ecf0f1;">
                            <strong>${log.asset_name}</strong> — ${log.action}
                            <span style="float:right;color:#999;font-size:0.8em;">${log.timestamp.split('T')[0]}</span>
                        </li>`;
                    });
                    html += '</ul>';
                    document.getElementById('audit-log').innerHTML = html;
                });
            }

            function renderRiskChart(levels) {
                const ctx = document.getElementById('riskChart').getContext('2d');
                if (riskChartInst) riskChartInst.destroy();
                const clrs = {CRITICAL:'#dc3545',HIGH:'#fd7e14',MEDIUM:'#ffc107',LOW:'#28a745'};
                riskChartInst = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: Object.keys(levels),
                        datasets: [{
                            data: Object.values(levels),
                            backgroundColor: Object.keys(levels).map(k => clrs[k] || '#667eea'),
                            borderWidth: 2
                        }]
                    },
                    options: { plugins: { legend: { position: 'bottom' } }, cutout: '60%' }
                });
            }

            function renderTypeChart(types) {
                const ctx = document.getElementById('typeChart').getContext('2d');
                if (typeChartInst) typeChartInst.destroy();
                typeChartInst = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: Object.keys(types),
                        datasets: [{ label: 'Assets', data: Object.values(types), backgroundColor: '#667eea', borderRadius: 4 }]
                    },
                    options: {
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                    }
                });
            }

            function loadAssets() {
                fetch('/api/assets').then(r => r.json()).then(data => {
                    const tbody = document.getElementById('assetsBody');
                    tbody.innerHTML = '';
                    if (!data.length) {
                        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#999;padding:20px;">No assets added yet.</td></tr>';
                        return;
                    }
                    data.forEach(asset => {
                        const isWeak = WEAK_ALGOS.some(w => asset.algorithm.toUpperCase().includes(w));
                        tbody.innerHTML += `<tr>
                            <td>${asset.id}</td>
                            <td>${asset.name}</td>
                            <td>${asset.asset_type}</td>
                            <td>${asset.algorithm}${isWeak ? ' <span style="color:#dc3545;font-size:0.8em;font-weight:bold;">⚠ Weak</span>' : ''}</td>
                            <td>${riskBadge(asset.risk_level)}</td>
                            <td>${asset.status}</td>
                            <td><button onclick="deleteAsset('${asset.id}')" style="background:#dc3545;color:white;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;">Delete</button></td>
                        </tr>`;
                    });
                });
            }

            function checkKeyLength() {
                const val = document.getElementById('keyLength').value;
                const warn = document.getElementById('keyLengthWarning');
                const input = document.getElementById('keyLength');
                if (!val || parseInt(val) === 0) {
                    warn.style.display = 'block';
                    input.style.borderColor = '#ffc107';
                } else if (parseInt(val) < 128) {
                    warn.innerHTML = '⚠️ Key length of <strong>' + val + ' bits</strong> is too short — minimum recommended is 128 bits.';
                    warn.style.cssText = 'display:block;margin-top:6px;font-size:0.9em;padding:8px 12px;border-radius:4px;border-left:4px solid #dc3545;background:#f8d7da;color:#721c24;';
                    input.style.borderColor = '#dc3545';
                } else {
                    warn.style.display = 'none';
                    input.style.borderColor = '#28a745';
                }
            }

            function checkAlgorithm() {
                const val = document.getElementById('algorithm').value;
                const warning = document.getElementById('algoWarning');
                const input = document.getElementById('algorithm');
                if (!val) { warning.style.display = 'none'; input.style.borderColor = ''; return; }
                const isWeak = WEAK_ALGOS.some(w => val.toUpperCase().includes(w));
                if (isWeak) {
                    warning.innerHTML = '⚠️ <strong>' + val + '</strong> is a weak or broken algorithm — this asset will be flagged as HIGH/CRITICAL risk and fail validation.';
                    warning.style.cssText = 'display:block;background:#f8d7da;color:#721c24;padding:10px 14px;border-radius:4px;margin-top:6px;font-size:0.9em;border-left:4px solid #dc3545;';
                    input.style.borderColor = '#dc3545';
                } else {
                    warning.innerHTML = '✓ Algorithm looks good.';
                    warning.style.cssText = 'display:block;background:#d4edda;color:#155724;padding:10px 14px;border-radius:4px;margin-top:6px;font-size:0.9em;border-left:4px solid #28a745;';
                    input.style.borderColor = '#28a745';
                }
            }

            function addAsset(e) {
                e.preventDefault();
                const feedback = document.getElementById('addFeedback');
                const payload = {
                    id: document.getElementById('assetId').value,
                    name: document.getElementById('assetName').value,
                    asset_type: document.getElementById('assetType').value,
                    algorithm: document.getElementById('algorithm').value,
                    key_length: parseInt(document.getElementById('keyLength').value) || 0,
                    status: document.getElementById('status').value
                };
                fetch('/api/assets', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                }).then(r => r.json()).then(res => {
                    if (res.success) {
                        const statusMsg = res.detected_status !== 'active'
                            ? ' (status auto-detected as <strong>' + res.detected_status + '</strong>)'
                            : '';
                        feedback.innerHTML = '\u2713 Asset <strong>' + payload.name + '</strong> added successfully!' + statusMsg;
                        feedback.style.cssText = 'display:block;background:#d4edda;color:#155724;padding:12px 16px;border-radius:4px;margin-top:15px;font-weight:600;';
                        e.target.reset();
                        document.getElementById('algoWarning').style.display = 'none';
                        document.getElementById('algorithm').style.borderColor = '';
                        document.getElementById('status').style.background = '';
                        loadDashboard();
                    } else {
                        feedback.innerHTML = '✗ Error: ' + res.error;
                        feedback.style.cssText = 'display:block;background:#f8d7da;color:#721c24;padding:12px 16px;border-radius:4px;margin-top:15px;font-weight:600;';
                    }
                    setTimeout(() => { feedback.style.display = 'none'; }, 4000);
                });
            }

            function deleteAsset(id) {
                if (confirm('Delete asset ' + id + '?')) {
                    fetch('/api/assets/' + id, {method: 'DELETE'}).then(r => r.json()).then(() => loadAssets());
                }
            }

            function validateBOM() {
                fetch('/api/validate/detail').then(r => r.json()).then(data => {
                    // Summary banner
                    const validCount  = data.assets.filter(a => a.valid).length;
                    const invalidCount = data.assets.filter(a => !a.valid).length;
                    const banner = document.getElementById('validationResult');
                    if (data.bom_valid) {
                        banner.innerHTML = '<div style="padding:14px;border-radius:6px;border-left:4px solid #28a745;background:#d4edda;color:#155724;"><strong>✓ BOM is valid!</strong> All ' + validCount + ' asset(s) passed.</div>';
                    } else {
                        banner.innerHTML = '<div style="padding:14px;border-radius:6px;border-left:4px solid #dc3545;background:#f8d7da;color:#721c24;"><strong>✗ Validation failed.</strong> ' + invalidCount + ' asset(s) have issues.</div>';
                    }

                    // Show chart + table
                    document.getElementById('validationChartWrap').style.display = 'block';

                    // Doughnut chart
                    const ctx = document.getElementById('validationChart').getContext('2d');
                    if (window._valChart) window._valChart.destroy();
                    window._valChart = new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Valid', 'Invalid'],
                            datasets: [{ data: [validCount, invalidCount], backgroundColor: ['#28a745','#dc3545'], borderWidth: 2 }]
                        },
                        options: {
                            plugins: {
                                legend: { position: 'bottom' },
                                tooltip: { callbacks: { label: ctx => ctx.label + ': ' + ctx.parsed } }
                            },
                            cutout: '60%'
                        }
                    });

                    // Per-asset table
                    let html = '<table><thead><tr><th>Asset ID</th><th>Name</th><th>Algorithm</th><th>Status</th><th>Result</th><th>Issues</th></tr></thead><tbody>';
                    data.assets.forEach(a => {
                        const ok = a.valid;
                        const resultCell = ok
                            ? '<td><span style="background:#28a745;color:white;padding:3px 8px;border-radius:10px;font-size:0.8em;">✓ Valid</span></td>'
                            : '<td><span style="background:#dc3545;color:white;padding:3px 8px;border-radius:10px;font-size:0.8em;">✗ Invalid</span></td>';
                        const issues = ok ? '<td style="color:#999;">—</td>' : '<td style="color:#dc3545;font-size:0.85em;">' + a.errors.join('<br>') + '</td>';
                        html += '<tr style="' + (ok ? '' : 'background:#fff5f5;') + '">' +
                            '<td>' + a.id + '</td>' +
                            '<td>' + a.name + '</td>' +
                            '<td>' + a.algorithm + '</td>' +
                            '<td>' + a.status + '</td>' +
                            resultCell + issues + '</tr>';
                    });
                    html += '</tbody></table>';
                    document.getElementById('assetValidationTable').innerHTML = html;
                });
            }

            function exportJSON() { window.location.href = '/api/export/json'; }
            function exportCSV()  { window.location.href = '/api/export/csv'; }

            function toggleScanPanel() {
                const p = document.getElementById('scanPanel');
                const a = document.getElementById('scanPanelArrow');
                if (p.style.display === 'none') { p.style.display = 'block'; a.innerHTML = '&#9650; collapse'; }
                else { p.style.display = 'none'; a.innerHTML = '&#9660; expand'; }
            }

            function scanWebsite() {
                const raw = document.getElementById('wsUrl').value.trim();
                if (!raw) { alert('Please enter a hostname.'); return; }
                document.getElementById('wsScanSpinner').style.display = 'block';
                document.getElementById('wsScanError').style.display = 'none';
                document.getElementById('wsScanAssets').style.display = 'none';
                document.getElementById('wsScanBtn').disabled = true;
                fetch('/api/scan-website', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: raw})
                }).then(r => r.json()).then(data => {
                    document.getElementById('wsScanSpinner').style.display = 'none';
                    document.getElementById('wsScanBtn').disabled = false;
                    if (data.error) {
                        const e = document.getElementById('wsScanError');
                        e.textContent = '\u2717 ' + data.error;
                        e.style.display = 'block';
                        return;
                    }
                    let html = '<p style="margin-bottom:8px;font-size:0.9em;color:#555;">Found <strong>' + data.assets.length + '</strong> asset(s). Click one to pre-fill the form below:</p>';
                    data.assets.forEach((a,i) => {
                        const risk = ['MD5','SHA-1','SHA1','DES','RC4','3DES','SSLv2','SSLv3','TLSv1','TLSv1.1'].some(w => a.algorithm.toUpperCase().includes(w.toUpperCase())) ? '#fd7e14' : '#28a745';
                        html += `<div onclick="prefillAsset(${i})" style="cursor:pointer;padding:10px 14px;border:1px solid #ddd;border-radius:6px;margin-bottom:8px;background:#f9f9f9;transition:background 0.2s;" onmouseover="this.style.background='#eef2ff'" onmouseout="this.style.background='#f9f9f9'">`
                            + `<span style="font-weight:600;">${a.name}</span> &nbsp;<span style="font-size:0.8em;color:#777;">${a.asset_type}</span><br>`
                            + `<span style="font-size:0.85em;">Algorithm: <strong>${a.algorithm}</strong>`
                            + (a.key_length ? ` &nbsp; Key bits: <strong>${a.key_length}</strong>` : '')
                            + (a.expiration_date ? ` &nbsp; Expires: <strong>${a.expiration_date}</strong>` : '')
                            + `</span></div>`;
                    });
                    const wrap = document.getElementById('wsScanAssets');
                    wrap.innerHTML = html;
                    wrap.style.display = 'block';
                    window._wsAssets = data.assets;
                }).catch(err => {
                    document.getElementById('wsScanSpinner').style.display = 'none';
                    document.getElementById('wsScanBtn').disabled = false;
                    const e = document.getElementById('wsScanError');
                    e.textContent = '\u2717 ' + err.message;
                    e.style.display = 'block';
                });
            }

            function prefillAsset(i) {
                const a = window._wsAssets[i];
                document.getElementById('assetId').value    = a.id;
                document.getElementById('assetName').value  = a.name;
                document.getElementById('assetType').value  = a.asset_type;
                document.getElementById('algorithm').value  = a.algorithm;
                document.getElementById('keyLength').value  = a.key_length || '';
                document.getElementById('status').value     = a.status || 'active';
                checkAlgorithm(); checkKeyLength();
                document.querySelector('.card form').scrollIntoView({behavior:'smooth'});
            }

            window.onload = loadDashboard;
        </script>
    </body>
    </html>
    """
    

    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/summary')
    def api_summary():
        summary = bom.get_summary()
        posture = CryptoBOMValidator.get_security_posture(bom)
        return jsonify({
            'total_assets': summary['total_assets'],
            'critical_risk': summary['critical_risk'],
            'vulnerable_assets': summary['vulnerable_assets'],
            'expired_assets': summary['expired_assets'],
            'security_score': int(posture['security_score'])
        })
    
    @app.route('/api/assets')
    def api_assets():
        return jsonify([{
            'id': asset.id,
            'name': asset.name,
            'asset_type': asset.asset_type,
            'algorithm': asset.algorithm,
            'risk_level': asset.risk_level(),
            'status': asset.status
        } for asset in bom.assets.values()])
    
    @app.route('/api/assets', methods=['POST'])
    def api_add_asset():
        try:
            data = request.json
            algorithm = data.get('algorithm', '')
            # Auto-detect status unless user explicitly chose deprecated/vulnerable/expired
            user_status = data.get('status', 'active')
            if user_status == 'active':
                auto_status = CryptoAsset.auto_detect_status(algorithm)
            else:
                auto_status = user_status
            asset = CryptoAsset(
                id=data['id'],
                name=data['name'],
                asset_type=data['asset_type'],
                algorithm=algorithm,
                key_length=data.get('key_length', 0),
                status=auto_status
            )
            bom.add_asset(asset)
            return jsonify({'success': True, 'detected_status': auto_status})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/assets/<asset_id>', methods=['DELETE'])
    def api_delete_asset(asset_id):
        try:
            bom.remove_asset(asset_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/audit-log')
    def api_audit_log():
        return jsonify([{
            'timestamp': log.timestamp,
            'action': log.action,
            'asset_id': log.asset_id,
            'asset_name': log.asset_name
        } for log in bom.audit_log[-10:]])
    
    @app.route('/api/validate/detail')
    def api_validate_detail():
        from .validator import CryptoValidator
        asset_results = []
        for asset in bom.assets.values():
            is_valid, errors = CryptoValidator.validate_asset(asset)
            asset_results.append({
                'id': asset.id,
                'name': asset.name,
                'algorithm': asset.algorithm,
                'status': asset.status,
                'valid': is_valid,
                'errors': errors
            })
        bom_valid = all(a['valid'] for a in asset_results)
        return jsonify({'bom_valid': bom_valid, 'assets': asset_results})

    @app.route('/api/chart-data')
    def api_chart_data():
        risk_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        type_counts = {}
        for asset in bom.assets.values():
            risk = asset.risk_level()
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
            type_counts[asset.asset_type] = type_counts.get(asset.asset_type, 0) + 1
        return jsonify({'risk_levels': risk_counts, 'asset_types': type_counts})

    @app.route('/api/validate')
    def api_validate():
        is_valid, messages = CryptoBOMValidator.validate_bom(bom)
        return jsonify({
            'valid': is_valid,
            'errors': messages if not is_valid else []
        })
    
    @app.route('/api/scan-website', methods=['POST'])
    def api_scan_website():
        import ssl, socket, datetime
        from urllib.parse import urlparse

        data = request.get_json(force=True, silent=True) or {}
        raw = (data.get('url') or '').strip()
        if not raw:
            return jsonify({'error': 'No URL provided'})
        if '://' not in raw:
            raw = 'https://' + raw
        try:
            parsed = urlparse(raw)
            hostname = parsed.hostname
            port = parsed.port or 443
            if not hostname:
                return jsonify({'error': 'Could not parse hostname'})
        except Exception as exc:
            return jsonify({'error': str(exc)})

        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as raw_sock:
                with ctx.wrap_socket(raw_sock, server_hostname=hostname) as ssock:
                    tls_ver  = ssock.version() or 'Unknown'
                    cipher   = ssock.cipher()
                    bits     = cipher[2] if cipher else 0
                    cert     = ssock.getpeercert()
                    def _rdn(seq):
                        out = {}
                        for rdn in seq:
                            for k, v in rdn:
                                out[k] = v.encode('ascii', 'replace').decode('ascii')
                        return out
                    subject  = _rdn(cert.get('subject',  ()))
                    expiry_str = ''
                    not_after  = cert.get('notAfter', '')
                    try:
                        expiry_dt  = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        expiry_str = expiry_dt.strftime('%Y-%m-%d')
                    except Exception:
                        pass
        except ssl.SSLError as exc:
            return jsonify({'error': f'TLS error: {exc}'})
        except OSError as exc:
            return jsonify({'error': f'Connection failed: {exc}'})
        except Exception as exc:
            return jsonify({'error': str(exc)})

        safe = hostname.replace('.', '-').replace('*', 'WILD').upper()
        tls_status = CryptoAsset.auto_detect_status(tls_ver)
        assets = [
            {
                'id':              f'TLS-{safe}',
                'name':            f'TLS on {hostname}',
                'asset_type':      'cipher_suite',
                'algorithm':       tls_ver,
                'key_length':      bits,
                'expiration_date': '',
                'status':          tls_status
            },
            {
                'id':              f'CERT-{safe}',
                'name':            f'Certificate for {hostname}',
                'asset_type':      'certificate',
                'algorithm':       'X.509',
                'key_length':      0,
                'expiration_date': expiry_str,
                'status':          'active'
            }
        ]
        return jsonify({'assets': assets})

    @app.route('/api/export/json')
    def api_export_json():
        tmp = os.path.join(tempfile.gettempdir(), 'cbom_export.json')
        bom.export_json(tmp)
        return send_file(tmp, as_attachment=True, download_name='cbom_export.json')
    
    @app.route('/api/export/csv')
    def api_export_csv():
        tmp = os.path.join(tempfile.gettempdir(), 'cbom_export.csv')
        bom.export_csv(tmp)
        return send_file(tmp, as_attachment=True, download_name='cbom_export.csv')

    return app


def create_web_ui(bom: Optional[CryptoBOM] = None, port: int = 5000):
    """Run the web UI locally — creates the app, opens a browser tab, starts the server."""
    try:
        app = create_app(bom)
    except ImportError as e:
        print(e)
        return

    port = int(os.environ.get('PORT', port))

    print(f"\n\u2713 C-BOM Web Interface Starting")
    print(f"  Open: http://localhost:{port}")
    print(f"  Press Ctrl+C to stop\n")

    try:
        webbrowser.open(f'http://localhost:{port}', new=1)
    except Exception:
        pass

    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
