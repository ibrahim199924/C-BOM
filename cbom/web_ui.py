"""
Web-based UI for C-BOM (Cryptographic Bill of Materials) using Flask
"""

import json
import webbrowser
from typing import Optional
from .models import CryptoAsset, CryptoBOM
from .validator import CryptoBOMValidator


def create_web_ui(bom: Optional[CryptoBOM] = None, port: int = 5000):
    """
    Create a web interface for C-BOM
    Requires Flask: pip install flask
    """
    try:
        from flask import Flask, render_template_string, request, jsonify, send_file
    except ImportError:
        print("Flask not installed. Install with: pip install flask")
        return
    
    app = Flask(__name__)
    
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
        </style>
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
                            <input type="text" id="algorithm" required>
                        </div>
                        <div class="form-group">
                            <label>Key Length</label>
                            <input type="number" id="keyLength">
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
                    </form>
                </div>
            </div>
            
            <div id="validate" class="section">
                <h2>Validate</h2>
                <div class="card">
                    <button class="primary" onclick="validateBOM()">Run Validation</button>
                    <div id="validationResult" style="margin-top: 20px;"></div>
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
            function showSection(id) {
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                document.getElementById(id).classList.add('active');
                if (id === 'dashboard') loadDashboard();
                else if (id === 'assets') loadAssets();
            }
            
            function loadDashboard() {
                fetch('/api/summary').then(r => r.json()).then(data => {
                    document.getElementById('summary').innerHTML = `
                        <div class="summary-box">
                            <div class="number">${data.total_assets}</div>
                            <div class="label">Total Assets</div>
                        </div>
                        <div class="summary-box">
                            <div class="number">${data.security_score}</div>
                            <div class="label">Security Score</div>
                        </div>
                        <div class="summary-box">
                            <div class="number">${data.critical_risk}</div>
                            <div class="label">Critical</div>
                        </div>
                        <div class="summary-box">
                            <div class="number">${data.vulnerable_assets}</div>
                            <div class="label">Vulnerable</div>
                        </div>
                    `;
                    fetch('/api/audit-log').then(r => r.json()).then(logs => {
                        let html = '<ul style="list-style: none;">';
                        logs.forEach(log => {
                            html += `<li style="padding: 10px; border-bottom: 1px solid #ecf0f1;">
                                <strong>${log.asset_name}</strong> - ${log.action} at ${log.timestamp}
                            </li>`;
                        });
                        html += '</ul>';
                        document.getElementById('audit-log').innerHTML = html;
                    });
                });
            }
            
            function loadAssets() {
                fetch('/api/assets').then(r => r.json()).then(data => {
                    const tbody = document.getElementById('assetsBody');
                    tbody.innerHTML = '';
                    data.forEach(asset => {
                        tbody.innerHTML += `
                            <tr>
                                <td>${asset.id}</td>
                                <td>${asset.name}</td>
                                <td>${asset.asset_type}</td>
                                <td>${asset.algorithm}</td>
                                <td><span class="badge">${asset.risk_level}</span></td>
                                <td>${asset.status}</td>
                                <td><button onclick="deleteAsset('${asset.id}')">Delete</button></td>
                            </tr>
                        `;
                    });
                });
            }
            
            function addAsset(e) {
                e.preventDefault();
                const data = {
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
                    body: JSON.stringify(data)
                }).then(r => r.json()).then(data => {
                    if (data.success) {
                        alert('Asset added!');
                        e.target.reset();
                        loadDashboard();
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }
            
            function deleteAsset(id) {
                if (confirm('Delete?')) {
                    fetch('/api/assets/' + id, {method: 'DELETE'})
                        .then(r => r.json()).then(data => loadAssets());
                }
            }
            
            function validateBOM() {
                fetch('/api/validate').then(r => r.json()).then(data => {
                    let html = '<div style="padding: 10px; border-radius: 4px; ' + 
                        (data.valid ? 'background: #d4edda;' : 'background: #f8d7da;') + '">';
                    if (data.valid) {
                        html += '✓ BOM is valid!';
                    } else {
                        html += '✗ Issues: ' + data.errors.join(', ');
                    }
                    html += '</div>';
                    document.getElementById('validationResult').innerHTML = html;
                });
            }
            
            function exportJSON() { window.location.href = '/api/export/json'; }
            function exportCSV() { window.location.href = '/api/export/csv'; }
            
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
            asset = CryptoAsset(
                id=data['id'],
                name=data['name'],
                asset_type=data['asset_type'],
                algorithm=data['algorithm'],
                key_length=data.get('key_length', 0),
                status=data.get('status', 'active')
            )
            bom.add_asset(asset)
            return jsonify({'success': True})
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
    
    @app.route('/api/validate')
    def api_validate():
        is_valid, messages = CryptoBOMValidator.validate_bom(bom)
        return jsonify({
            'valid': is_valid,
            'errors': messages if not is_valid else []
        })
    
    @app.route('/api/export/json')
    def api_export_json():
        bom.export_json('/tmp/cbom_export.json')
        return send_file('/tmp/cbom_export.json', as_attachment=True, download_name='cbom_export.json')
    
    @app.route('/api/export/csv')
    def api_export_csv():
        bom.export_csv('/tmp/cbom_export.csv')
        return send_file('/tmp/cbom_export.csv', as_attachment=True, download_name='cbom_export.csv')
    
    print(f"\n✓ C-BOM Web Interface Starting")
    print(f"  Open: http://localhost:{port}")
    print(f"  Press Ctrl+C to stop\n")
    
    try:
        webbrowser.open(f'http://localhost:{port}', new=1)
    except:
        pass
    
    app.run(debug=False, port=port, use_reloader=False)
