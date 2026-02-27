"""
Web-based UI for C-BOM (Cryptographic Bill of Materials) using Flask
"""

import json
import os
import secrets
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
        from flask import Flask, render_template_string, request, jsonify, send_file, session
    except ImportError:
        raise ImportError("Flask not installed. Install with: pip install flask")

    app = Flask(__name__)
    app.json.ensure_ascii = True  # prevent surrogate/non-ASCII encode errors
    # Use SECRET_KEY env var in production; fall back to a random key for local use
    app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # Per-session BOM store: session_id -> CryptoBOM
    _user_boms: dict = {}

    def get_user_bom() -> CryptoBOM:
        """Return the BOM for the current browser session, creating one if needed."""
        sid = session.get('sid')
        if not sid or sid not in _user_boms:
            sid = secrets.token_hex(16)
            session['sid'] = sid
            session.permanent = False
            _user_boms[sid] = CryptoBOM("C-BOM Web Project", "Cryptographic Asset Inventory")
        return _user_boms[sid]

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
            /* Preset sidebar */
            .preset-group-title {
                font-size: 0.72em;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                color: #aaa;
                padding: 10px 14px 4px;
                font-weight: 700;
            }
            .preset-item {
                padding: 8px 14px;
                cursor: pointer;
                font-size: 0.86em;
                border-left: 3px solid transparent;
                transition: all 0.15s;
                display: flex;
                align-items: center;
                gap: 8px;
                color: #444;
            }
            .preset-item:hover, .preset-item.selected {
                background: #eef2ff;
                border-left-color: #667eea;
                color: #667eea;
            }
            .preset-badge {
                margin-left: auto;
                font-size: 0.7em;
                padding: 2px 6px;
                border-radius: 8px;
                font-weight: 700;
                white-space: nowrap;
            }
            /* Autocomplete */
            .autocomplete-wrap { position: relative; }
            .autocomplete-list {
                position: absolute;
                top: 100%;
                left: 0; right: 0;
                background: white;
                border: 1px solid #ddd;
                border-top: none;
                border-radius: 0 0 6px 6px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.12);
                z-index: 200;
                max-height: 220px;
                overflow-y: auto;
            }
            .autocomplete-item {
                padding: 8px 12px;
                cursor: pointer;
                font-size: 0.86em;
                border-bottom: 1px solid #f0f0f0;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .autocomplete-item:hover { background: #eef2ff; }
            .ac-name { font-weight: 600; min-width: 160px; flex-shrink: 0; }
            .ac-desc { color: #888; font-size: 0.9em; }
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

                <!-- Scanner panel -->
                <div class="card" style="margin-bottom:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;cursor:pointer;" onclick="toggleScanPanel()">
                        <strong>🌐 Read assets from a website</strong>
                        <span id="scanPanelArrow" style="font-size:0.85em;color:#667eea;">&#9660; expand</span>
                    </div>
                    <div id="scanPanel" style="display:none;margin-top:14px;">
                        <p style="color:#666;font-size:0.9em;margin-bottom:10px;">Enter a hostname — the scanner will analyse TLS version, cipher suite, public key type &amp; strength, certificate validity, signature algorithm, and quantum risk, then pre-fill assets below.</p>
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

                <!-- Two-column: preset sidebar + form -->
                <div style="display:grid;grid-template-columns:270px 1fr;gap:16px;align-items:start;">

                    <!-- LEFT SIDEBAR -->
                    <div>
                        <div class="card" style="margin:0;padding:0;overflow:hidden;">
                            <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:11px 16px;font-weight:700;font-size:0.92em;">⚡ Quick Presets</div>
                            <div id="presetList" style="max-height:420px;overflow-y:auto;"></div>
                        </div>
                        <div class="card" id="presetInfo" style="margin-top:12px;padding:14px;min-height:100px;">
                            <div id="presetInfoContent" style="color:#aaa;font-size:0.85em;text-align:center;padding:16px 0;">
                                ← Hover a preset to learn what it means
                            </div>
                        </div>
                    </div>

                    <!-- RIGHT: FORM -->
                    <div class="card" style="margin:0;">
                        <form onsubmit="addAsset(event)">
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                                <div class="form-group" style="margin:0;">
                                    <label>Name *</label>
                                    <input type="text" id="assetName" required placeholder="e.g. Production TLS Certificate">
                                </div>
                                <div class="form-group" style="margin:0;">
                                    <label>Asset ID <span style="color:#999;font-weight:normal;">(auto if blank)</span></label>
                                    <input type="text" id="assetId" placeholder="Auto-generated">
                                </div>
                            </div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px;">
                                <div class="form-group" style="margin:0;">
                                    <label>Type *</label>
                                    <select id="assetType" required>
                                        <option value="">Select type</option>
                                        <option value="algorithm">Algorithm</option>
                                        <option value="key">Key</option>
                                        <option value="certificate">Certificate</option>
                                        <option value="cipher_suite">Cipher Suite</option>
                                        <option value="library">Library</option>
                                        <option value="protocol">Protocol</option>
                                    </select>
                                </div>
                                <div class="form-group" style="margin:0;">
                                    <label>Status</label>
                                    <select id="status">
                                        <option value="active">Active</option>
                                        <option value="deprecated">Deprecated</option>
                                        <option value="vulnerable">Vulnerable</option>
                                        <option value="expired">Expired</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group autocomplete-wrap" style="margin-top:12px;">
                                <label>Algorithm *</label>
                                <input type="text" id="algorithm" required autocomplete="off"
                                    placeholder="e.g. AES-256-GCM, RSA-4096, Ed25519 — type to search"
                                    oninput="checkAlgorithm();showAlgoSuggestions(this.value)"
                                    onblur="setTimeout(()=>document.getElementById('algoList').style.display='none',150)">
                                <div id="algoList" class="autocomplete-list" style="display:none;"></div>
                                <div id="algoWarning" class="algo-warning"></div>
                            </div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:4px;">
                                <div class="form-group" style="margin:0;">
                                    <label>Key Length <span style="color:#999;font-weight:normal;">(bits)</span></label>
                                    <input type="number" id="keyLength" oninput="checkKeyLength()" onblur="checkKeyLength()" placeholder="e.g. 256">
                                    <div id="keyLengthWarning" style="display:none;margin-top:6px;font-size:0.9em;padding:8px 12px;border-radius:4px;border-left:4px solid #ffc107;background:#fff3cd;color:#856404;">
                                        ⚠️ Key length is recommended — without it, validation may flag this asset.
                                    </div>
                                </div>
                                <div class="form-group" style="margin:0;">
                                    <label>Expiration Date <span style="color:#999;font-weight:normal;">(optional)</span></label>
                                    <input type="date" id="expirationDate">
                                </div>
                            </div>
                            <div style="display:flex;gap:10px;margin-top:16px;align-items:center;">
                                <button type="submit" class="primary">➕ Add Asset</button>
                                <button type="button" onclick="clearAssetForm()" style="background:#6c757d;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;font-weight:600;">✕ Clear</button>
                            </div>
                            <div id="addFeedback" class="add-feedback"></div>
                        </form>
                    </div>
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

            // ── Preset definitions ──────────────────────────────────────────────
            const PRESETS = [
              { group: '🔐 Certificates', items: [
                { label:'RSA-2048 Certificate',   key:'rsa2048cert',   badge:'ACCEPTABLE', bc:'#ffc107', bt:'#333',
                  fill:{name:'RSA-2048 Certificate',type:'certificate',algo:'RSA-2048',bits:2048,status:'active'},
                  info:{icon:'🔐',title:'RSA-2048 Certificate',security:'ACCEPTABLE',quantumSafe:false,
                    what:'A digital certificate using a 2048-bit RSA public key. RSA is the most widely deployed asymmetric algorithm, used for authentication and secure key exchange over HTTPS.',
                    uses:'HTTPS, code signing, email (S/MIME), VPN',
                    warn:'RSA-2048 is the current minimum. Migrate to RSA-4096 or ECDSA P-256 for new deployments.'}},
                { label:'RSA-4096 Certificate',   key:'rsa4096cert',   badge:'STRONG',     bc:'#28a745', bt:'white',
                  fill:{name:'RSA-4096 Certificate',type:'certificate',algo:'RSA-4096',bits:4096,status:'active'},
                  info:{icon:'🔐',title:'RSA-4096 Certificate',security:'STRONG',quantumSafe:false,
                    what:'A certificate using a 4096-bit RSA key. Stronger than RSA-2048 with a larger key, providing better long-term security at the cost of slightly slower handshakes.',
                    uses:'Root CAs, long-lived certificates, enterprise environments',
                    warn:"Still vulnerable to quantum computers via Shor's algorithm."}},
                { label:'ECDSA P-256 Certificate', key:'ecdsa256cert',  badge:'RECOMMENDED',bc:'#28a745', bt:'white',
                  fill:{name:'ECDSA P-256 Certificate',type:'certificate',algo:'ECDSA-P256',bits:256,status:'active'},
                  info:{icon:'🔐',title:'ECDSA P-256 Certificate',security:'RECOMMENDED',quantumSafe:false,
                    what:'Certificate using Elliptic Curve DSA on NIST P-256. Provides 128-bit security with much smaller key sizes than RSA — faster TLS handshakes and lower overhead.',
                    uses:'Modern HTTPS, mTLS, API authentication, TLS 1.3',
                    warn:null}},
                { label:'ECDSA P-384 Certificate', key:'ecdsa384cert',  badge:'RECOMMENDED',bc:'#28a745', bt:'white',
                  fill:{name:'ECDSA P-384 Certificate',type:'certificate',algo:'ECDSA-P384',bits:384,status:'active'},
                  info:{icon:'🔐',title:'ECDSA P-384 Certificate',security:'RECOMMENDED',quantumSafe:false,
                    what:'ECDSA certificate on NIST P-384 (192-bit security). Required by NSA Suite B and used in high-security government and financial environments.',
                    uses:'Government/military, financial sector, NSA Suite B compliance',
                    warn:null}},
                { label:'Ed25519 Certificate',     key:'ed25519cert',   badge:'BEST',       bc:'#20c997', bt:'white',
                  fill:{name:'Ed25519 Certificate',type:'certificate',algo:'Ed25519',bits:256,status:'active'},
                  info:{icon:'🔐',title:'Ed25519 Certificate',security:'BEST',quantumSafe:false,
                    what:'EdDSA signature scheme on Curve25519. Designed to be fast, compact, and free from implementation pitfalls — constant-time by construction and resistant to side-channel attacks.',
                    uses:'SSH keys, modern TLS, Signal protocol, blockchain',
                    warn:'Not yet accepted by all CA/Browser Forum policies for public HTTPS certs.'}},
              ]},
              { group: '🔑 Symmetric Keys', items: [
                { label:'AES-256 Key',   key:'aes256',   badge:'RECOMMENDED',bc:'#28a745', bt:'white',
                  fill:{name:'AES-256 Encryption Key',type:'key',algo:'AES-256-GCM',bits:256,status:'active'},
                  info:{icon:'🔑',title:'AES-256 Key',security:'RECOMMENDED',quantumSafe:true,
                    what:'256-bit key for AES (Advanced Encryption Standard) in GCM mode. The global gold standard for symmetric encryption, used everywhere from TLS to full-disk encryption.',
                    uses:'File/disk encryption, TLS record layer, database secrets, cloud storage',
                    warn:null}},
                { label:'AES-128 Key',   key:'aes128',   badge:'ACCEPTABLE', bc:'#ffc107', bt:'#333',
                  fill:{name:'AES-128 Encryption Key',type:'key',algo:'AES-128-GCM',bits:128,status:'active'},
                  info:{icon:'🔑',title:'AES-128 Key',security:'ACCEPTABLE',quantumSafe:false,
                    what:"128-bit AES-GCM key. Secure today, but Grover's quantum algorithm halves effective security to 64 bits, which is considered marginal for long-term data.",
                    uses:'TLS, performance-critical apps, IoT devices with limited memory',
                    warn:'Prefer AES-256 for new deployments or long-lived data.'}},
                { label:'ChaCha20 Key',  key:'chacha20', badge:'RECOMMENDED',bc:'#28a745', bt:'white',
                  fill:{name:'ChaCha20-Poly1305 Key',type:'key',algo:'ChaCha20-Poly1305',bits:256,status:'active'},
                  info:{icon:'🔑',title:'ChaCha20-Poly1305',security:'RECOMMENDED',quantumSafe:true,
                    what:'256-bit stream cipher by Daniel Bernstein. Preferred on devices without hardware AES acceleration. ChaCha20 handles encryption; Poly1305 handles authentication.',
                    uses:'Mobile TLS, WireGuard VPN, Signal protocol, embedded/IoT',
                    warn:null}},
                { label:'HMAC-SHA256',   key:'hmacsha256',badge:'RECOMMENDED',bc:'#28a745', bt:'white',
                  fill:{name:'HMAC-SHA256 Key',type:'key',algo:'HMAC-SHA256',bits:256,status:'active'},
                  info:{icon:'🔑',title:'HMAC-SHA256',security:'RECOMMENDED',quantumSafe:true,
                    what:"Keyed-Hash Message Authentication Code using SHA-256. Verifies both the integrity (the data wasn't changed) and authenticity (sent by a trusted party) of a message.",
                    uses:'API authentication tokens, JWTs, webhook signatures, cookie MAC',
                    warn:null}},
              ]},
              { group: '🔄 Key Exchange', items: [
                { label:'X25519 Key',       key:'x25519',    badge:'BEST',       bc:'#20c997', bt:'white',
                  fill:{name:'X25519 Key Exchange Key',type:'key',algo:'X25519',bits:256,status:'active'},
                  info:{icon:'🔄',title:'X25519',security:'BEST',quantumSafe:false,
                    what:'Diffie-Hellman key exchange over Curve25519. Designed by Bernstein for efficiency and safety — constant-time to resist timing attacks, no weak parameters.',
                    uses:'TLS 1.3 key exchange, WireGuard, Signal, modern SSH',
                    warn:'Still quantum-vulnerable. Post-quantum replacement: ML-KEM (CRYSTALS-Kyber, FIPS 203).'}},
                { label:'ECDH P-256 Key',   key:'ecdh256',   badge:'RECOMMENDED',bc:'#28a745', bt:'white',
                  fill:{name:'ECDH P-256 Key',type:'key',algo:'ECDH-P256',bits:256,status:'active'},
                  info:{icon:'🔄',title:'ECDH P-256',security:'RECOMMENDED',quantumSafe:false,
                    what:'Elliptic Curve Diffie-Hellman over NIST P-256. Allows two parties to establish a shared secret without transmitting it, providing forward secrecy when used ephemerally.',
                    uses:'TLS key exchange, secure messaging, mutual authentication',
                    warn:null}},
                { label:'RSA-2048 Key',     key:'rsa2048key',badge:'ACCEPTABLE', bc:'#ffc107', bt:'#333',
                  fill:{name:'RSA-2048 Key',type:'key',algo:'RSA-2048',bits:2048,status:'active'},
                  info:{icon:'🔑',title:'RSA-2048 Key',security:'ACCEPTABLE',quantumSafe:false,
                    what:'2048-bit RSA asymmetric key for encryption or signing. The minimum NIST-recommended RSA size. Security relies on the difficulty of factoring large integers.',
                    uses:'Email encryption (PGP/GPG), code signing, legacy TLS, SSH host keys',
                    warn:'Prefer ECDSA P-256 or Ed25519 for new keys — same security, smaller size.'}},
                { label:'ML-KEM-768 (Post-Quantum)', key:'mlkem768', badge:'PQC', bc:'#6f42c1', bt:'white',
                  fill:{name:'ML-KEM-768 Key',type:'key',algo:'ML-KEM-768',bits:768,status:'active'},
                  info:{icon:'🛡️',title:'ML-KEM-768 (CRYSTALS-Kyber)',security:'RECOMMENDED',quantumSafe:true,
                    what:'NIST FIPS 203 post-quantum key encapsulation mechanism based on the CRYSTALS-Kyber lattice problem. Designed to replace RSA and ECDH key exchange against quantum attacks.',
                    uses:'Post-quantum TLS, hybrid key exchange, future-proof key transport',
                    warn:'Not yet universally supported — use in hybrid alongside ECDH for compatibility.'}},
              ]},
              { group: '🌐 Cipher Suites', items: [
                { label:'TLS 1.3 AES-256-GCM',    key:'tls13_aes256',  badge:'BEST', bc:'#20c997', bt:'white',
                  fill:{name:'TLS 1.3 AES-256-GCM-SHA384',type:'cipher_suite',algo:'TLS_AES_256_GCM_SHA384',bits:256,status:'active'},
                  info:{icon:'🌐',title:'TLS_AES_256_GCM_SHA384',security:'BEST',quantumSafe:false,
                    what:'Top-tier TLS 1.3 cipher suite. TLS 1.3 mandates forward secrecy, removes legacy options, and simplifies the handshake. AES-256-GCM provides authenticated encryption.',
                    uses:'HTTPS, mTLS, gRPC, REST APIs, secure webhooks',
                    warn:null}},
                { label:'TLS 1.3 ChaCha20',         key:'tls13_chacha', badge:'BEST', bc:'#20c997', bt:'white',
                  fill:{name:'TLS 1.3 ChaCha20-Poly1305',type:'cipher_suite',algo:'TLS_CHACHA20_POLY1305_SHA256',bits:256,status:'active'},
                  info:{icon:'🌐',title:'TLS_CHACHA20_POLY1305_SHA256',security:'BEST',quantumSafe:false,
                    what:'TLS 1.3 suite using ChaCha20-Poly1305. Preferred on mobile and embedded devices without AES hardware, offering comparable security to AES-256-GCM.',
                    uses:'Mobile HTTPS, IoT, Android, WireGuard',
                    warn:null}},
                { label:'TLS 1.2 ECDHE-AES256',     key:'tls12_ecdhe256',badge:'ACCEPTABLE',bc:'#ffc107',bt:'#333',
                  fill:{name:'TLS 1.2 ECDHE-AES256-GCM-SHA384',type:'cipher_suite',algo:'ECDHE-ECDSA-AES256-GCM-SHA384',bits:256,status:'active'},
                  info:{icon:'🌐',title:'ECDHE-ECDSA-AES256-GCM-SHA384',security:'ACCEPTABLE',quantumSafe:false,
                    what:'Strong TLS 1.2 cipher suite with ephemeral ECDH key exchange and AES-256-GCM encryption. Provides forward secrecy. Only use TLS 1.2 for legacy compatibility.',
                    uses:'HTTPS on servers needing backwards compatibility',
                    warn:'Upgrade to TLS 1.3 where possible.'}},
              ]},
              { group: '#️⃣ Hash Algorithms', items: [
                { label:'SHA-256',  key:'sha256',   badge:'RECOMMENDED',bc:'#28a745',bt:'white',
                  fill:{name:'SHA-256 Hash',type:'algorithm',algo:'SHA-256',bits:256,status:'active'},
                  info:{icon:'#️⃣',title:'SHA-256',security:'RECOMMENDED',quantumSafe:true,
                    what:"256-bit hash from the SHA-2 family (NIST). Produces a fixed-size fingerprint of any data. Collision-resistant — it's computationally infeasible to find two inputs with the same hash.",
                    uses:'Code signing, certificate fingerprints, Bitcoin, file integrity, git commits',
                    warn:null}},
                { label:'SHA-512',  key:'sha512',   badge:'RECOMMENDED',bc:'#28a745',bt:'white',
                  fill:{name:'SHA-512 Hash',type:'algorithm',algo:'SHA-512',bits:512,status:'active'},
                  info:{icon:'#️⃣',title:'SHA-512',security:'RECOMMENDED',quantumSafe:true,
                    what:'512-bit SHA-2 variant. Stronger than SHA-256 and actually faster on 64-bit hardware. Common in high-security signature schemes and password stretching.',
                    uses:'High-security signatures, HMAC, password hashing pipelines',
                    warn:null}},
                { label:'SHA3-256', key:'sha3256',  badge:'RECOMMENDED',bc:'#28a745',bt:'white',
                  fill:{name:'SHA3-256 Hash',type:'algorithm',algo:'SHA3-256',bits:256,status:'active'},
                  info:{icon:'#️⃣',title:'SHA3-256 (Keccak)',security:'RECOMMENDED',quantumSafe:true,
                    what:'SHA-3 uses the Keccak sponge construction — completely different internal design from SHA-2. NIST standardised it in 2015 to provide algorithm diversity.',
                    uses:'Ethereum hashing, post-quantum hybrid schemes, regulatory diversity',
                    warn:null}},
                { label:'BLAKE3',   key:'blake3',   badge:'RECOMMENDED',bc:'#28a745',bt:'white',
                  fill:{name:'BLAKE3 Hash',type:'algorithm',algo:'BLAKE3',bits:256,status:'active'},
                  info:{icon:'#️⃣',title:'BLAKE3',security:'RECOMMENDED',quantumSafe:true,
                    what:'The fastest modern cryptographic hash function — often 5-10x faster than SHA-256. Supports keying (MAC), key derivation, and XOF (extendable output) in a single primitive.',
                    uses:'High-throughput integrity checks, streaming, Merkle trees, deduplication',
                    warn:null}},
              ]},
              { group: '⚠️ Legacy (for inventory)', items: [
                { label:'MD5',      key:'md5',  badge:'BROKEN',    bc:'#dc3545',bt:'white',
                  fill:{name:'MD5 Hash',type:'algorithm',algo:'MD5',bits:128,status:'vulnerable'},
                  info:{icon:'⚠️',title:'MD5 — BROKEN',security:'BROKEN',quantumSafe:false,
                    what:'128-bit hash function, completely broken for cryptographic use since 2008. Collision attacks are practical on consumer hardware. Never use for signatures, certificates, or passwords.',
                    uses:'Non-security checksums only (checksumming downloaded files is acceptable, but not security-critical data)',
                    warn:'Replace with SHA-256. MD5 signatures and certificates are rejected by all modern systems.'}},
                { label:'SHA-1',    key:'sha1', badge:'DEPRECATED', bc:'#fd7e14',bt:'white',
                  fill:{name:'SHA-1 Hash',type:'algorithm',algo:'SHA-1',bits:160,status:'deprecated'},
                  info:{icon:'⚠️',title:'SHA-1 — DEPRECATED',security:'DEPRECATED',quantumSafe:false,
                    what:'160-bit hash, deprecated by NIST in 2011. The SHAttered attack (2017) demonstrated practical SHA-1 chosen-prefix collisions. CAs stopped issuing SHA-1 certs years ago.',
                    uses:'Legacy systems only — migrate all SHA-1 usages to SHA-256+',
                    warn:'SHA-1 collision attacks are practical. Immediate migration is required.'}},
                { label:'3DES',     key:'des',  badge:'DEPRECATED', bc:'#fd7e14',bt:'white',
                  fill:{name:'3DES Cipher',type:'algorithm',algo:'3DES',bits:112,status:'deprecated'},
                  info:{icon:'⚠️',title:'3DES — DEPRECATED',security:'DEPRECATED',quantumSafe:false,
                    what:'Triple-DES extends DES to ~112-bit effective security but is slow and vulnerable to the SWEET32 birthday attack at 64-bit block size. NIST deprecated it effective December 2023.',
                    uses:'Legacy banking/POS systems only — replace with AES-256',
                    warn:'NIST deprecated 3DES through 2023 (SP 800-131A). Must be replaced.'}},
                { label:'RC4',      key:'rc4',  badge:'BROKEN',    bc:'#dc3545',bt:'white',
                  fill:{name:'RC4 Stream Cipher',type:'algorithm',algo:'RC4',bits:128,status:'vulnerable'},
                  info:{icon:'⚠️',title:'RC4 — BROKEN',security:'BROKEN',quantumSafe:false,
                    what:'RC4 has multiple known key-scheduling biases and statistical weaknesses. Statistical attacks can recover plaintext from enough ciphertext. Prohibited by RFC 7465 in TLS.',
                    uses:'None — RC4 must not be used anywhere',
                    warn:'RC4 is banned in TLS (RFC 7465). Remove from all systems immediately.'}},
              ]},
            ];

            // ── Algorithm autocomplete data ─────────────────────────────────────
            const KNOWN_ALGOS = [
              {name:'AES-256-GCM',                      bits:256,  type:'key',         desc:'AES 256-bit GCM — recommended symmetric encryption'},
              {name:'AES-128-GCM',                      bits:128,  type:'key',         desc:'AES 128-bit GCM — fast, widely supported'},
              {name:'AES-256-CBC',                      bits:256,  type:'key',         desc:'AES 256-bit CBC — requires careful IV management'},
              {name:'AES-128-CBC',                      bits:128,  type:'key',         desc:'AES 128-bit CBC — legacy applications'},
              {name:'ChaCha20-Poly1305',                bits:256,  type:'key',         desc:'Stream cipher — ideal for mobile/IoT without hardware AES'},
              {name:'HMAC-SHA256',                      bits:256,  type:'key',         desc:'Message authentication with SHA-256'},
              {name:'HMAC-SHA512',                      bits:512,  type:'key',         desc:'Message authentication with SHA-512'},
              {name:'RSA-2048',                         bits:2048, type:'key',         desc:'Minimum acceptable RSA — 112-bit security'},
              {name:'RSA-3072',                         bits:3072, type:'key',         desc:'RSA with 128-bit security — NIST transition target'},
              {name:'RSA-4096',                         bits:4096, type:'key',         desc:'Strong RSA — good for long-lived assets'},
              {name:'ECDSA-P256',                       bits:256,  type:'key',         desc:'EC signature NIST P-256 — recommended'},
              {name:'ECDSA-P384',                       bits:384,  type:'key',         desc:'EC signature NIST P-384 — high security'},
              {name:'ECDSA-P521',                       bits:521,  type:'key',         desc:'EC signature NIST P-521 — maximum ECC'},
              {name:'Ed25519',                          bits:256,  type:'key',         desc:'Modern EdDSA — fast, safe, compact'},
              {name:'Ed448',                            bits:448,  type:'key',         desc:'EdDSA on Curve448 — highest EdDSA security'},
              {name:'X25519',                           bits:256,  type:'key',         desc:'Key exchange over Curve25519 — preferred DH'},
              {name:'ECDH-P256',                        bits:256,  type:'key',         desc:'Elliptic curve DH, NIST P-256'},
              {name:'ECDH-P384',                        bits:384,  type:'key',         desc:'Elliptic curve DH, NIST P-384'},
              {name:'DSA-2048',                         bits:2048, type:'key',         desc:'⚠️ Deprecated — replace with ECDSA or Ed25519'},
              {name:'ML-KEM-768',                       bits:768,  type:'key',         desc:'Post-quantum KEM (CRYSTALS-Kyber) — FIPS 203'},
              {name:'ML-KEM-1024',                      bits:1024, type:'key',         desc:'Post-quantum KEM level 5 — max security, FIPS 203'},
              {name:'ML-DSA-65',                        bits:256,  type:'key',         desc:'Post-quantum signatures (Dilithium) — FIPS 204'},
              {name:'SLH-DSA-SHA2-128s',                bits:128,  type:'key',         desc:'Post-quantum hash-based signatures — FIPS 205'},
              {name:'SHA-256',                          bits:256,  type:'algorithm',   desc:'SHA-2 256-bit — widely recommended'},
              {name:'SHA-384',                          bits:384,  type:'algorithm',   desc:'SHA-2 384-bit'},
              {name:'SHA-512',                          bits:512,  type:'algorithm',   desc:'SHA-2 512-bit — strongest SHA-2'},
              {name:'SHA3-256',                         bits:256,  type:'algorithm',   desc:'NIST SHA-3 standard, 256-bit (Keccak)'},
              {name:'SHA3-512',                         bits:512,  type:'algorithm',   desc:'NIST SHA-3 standard, 512-bit'},
              {name:'BLAKE2b',                          bits:512,  type:'algorithm',   desc:'Fast modern hash — alternative to SHA-2'},
              {name:'BLAKE3',                           bits:256,  type:'algorithm',   desc:'Fastest cryptographic hash — modern alternative'},
              {name:'SHA-1',                            bits:160,  type:'algorithm',   desc:'⚠️ Deprecated — collision attacks known'},
              {name:'MD5',                              bits:128,  type:'algorithm',   desc:'❌ Broken — never use for security'},
              {name:'TLS_AES_256_GCM_SHA384',           bits:256,  type:'cipher_suite',desc:'TLS 1.3 — best practice'},
              {name:'TLS_AES_128_GCM_SHA256',           bits:128,  type:'cipher_suite',desc:'TLS 1.3 — standard'},
              {name:'TLS_CHACHA20_POLY1305_SHA256',      bits:256,  type:'cipher_suite',desc:'TLS 1.3 — ideal for mobile'},
              {name:'ECDHE-ECDSA-AES256-GCM-SHA384',    bits:256,  type:'cipher_suite',desc:'TLS 1.2 — strong, forward secrecy'},
              {name:'ECDHE-RSA-AES256-GCM-SHA384',      bits:256,  type:'cipher_suite',desc:'TLS 1.2 — strong with RSA auth'},
              {name:'ECDHE-ECDSA-AES128-GCM-SHA256',    bits:128,  type:'cipher_suite',desc:'TLS 1.2 — balanced'},
              {name:'3DES',                             bits:112,  type:'algorithm',   desc:'⚠️ Deprecated — replace with AES'},
              {name:'RC4',                              bits:128,  type:'algorithm',   desc:'❌ Broken — RFC 7465 prohibited in TLS'},
              {name:'DES',                              bits:56,   type:'algorithm',   desc:'❌ 56-bit — completely broken'},
              {name:'TLSv1.3',                          bits:0,    type:'protocol',    desc:'Current TLS standard — recommended'},
              {name:'TLSv1.2',                          bits:0,    type:'protocol',    desc:'Acceptable — migrate to TLS 1.3 where possible'},
              {name:'TLSv1.1',                          bits:0,    type:'protocol',    desc:'⚠️ Deprecated — RFC 8996'},
              {name:'TLSv1',                            bits:0,    type:'protocol',    desc:'⚠️ Deprecated — RFC 8996'},
              {name:'SSLv3',                            bits:0,    type:'protocol',    desc:'❌ Broken — POODLE attack'},
            ];

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

            // ── Render preset sidebar ───────────────────────────────────────────
            function renderPresets() {
                const SECURITY_COLORS = {BEST:'#20c997',RECOMMENDED:'#28a745',ACCEPTABLE:'#ffc107',STRONG:'#28a745',DEPRECATED:'#fd7e14',BROKEN:'#dc3545',PQC:'#6f42c1'};
                const SECURITY_TEXT   = {BEST:'white',RECOMMENDED:'white',ACCEPTABLE:'#333',STRONG:'white',DEPRECATED:'white',BROKEN:'white',PQC:'white'};
                let html = '';
                PRESETS.forEach(group => {
                    html += '<div class="preset-group-title">' + group.group + '</div>';
                    group.items.forEach(p => {
                        const bc = p.bc, bt = p.bt;
                        html += '<div class="preset-item" data-preset="' + p.key + '" '
                            + 'onmouseenter="showPresetInfo(\'' + p.key + '\')" '
                            + 'onclick="applyPreset(\'' + p.key + '\')">'
                            + '<span>' + p.label + '</span>'
                            + '<span class="preset-badge" style="background:' + bc + ';color:' + bt + ';">' + p.badge + '</span>'
                            + '</div>';
                    });
                });
                document.getElementById('presetList').innerHTML = html;
            }

            function applyPreset(key) {
                const preset = PRESETS.flatMap(g => g.items).find(p => p.key === key);
                if (!preset) return;
                const f = preset.fill;
                document.getElementById('assetName').value  = f.name;
                document.getElementById('assetType').value  = f.type;
                document.getElementById('algorithm').value  = f.algo;
                document.getElementById('keyLength').value  = f.bits || '';
                document.getElementById('status').value     = f.status;
                document.getElementById('assetId').value    = '';
                document.getElementById('expirationDate').value = '';
                checkAlgorithm(); checkKeyLength();
                document.querySelectorAll('.preset-item').forEach(el => el.classList.remove('selected'));
                const el = document.querySelector('[data-preset="' + key + '"]');
                if (el) el.classList.add('selected');
                showPresetInfo(key);
            }

            function showPresetInfo(key) {
                const preset = PRESETS.flatMap(g => g.items).find(p => p.key === key);
                if (!preset) return;
                const info = preset.info;
                const SC = {BEST:'#20c997',RECOMMENDED:'#28a745',ACCEPTABLE:'#ffc107',STRONG:'#28a745',DEPRECATED:'#fd7e14',BROKEN:'#dc3545',PQC:'#6f42c1'};
                const ST = {BEST:'white',RECOMMENDED:'white',ACCEPTABLE:'#333',STRONG:'white',DEPRECATED:'white',BROKEN:'white',PQC:'white'};
                const sc = SC[info.security]||'#6c757d', stc = ST[info.security]||'white';
                let html = '<div style="font-size:0.86em;">'
                    + '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
                    + '<strong>' + info.icon + ' ' + info.title + '</strong>'
                    + '<span style="background:' + sc + ';color:' + stc + ';padding:2px 8px;border-radius:8px;font-size:0.76em;font-weight:700;">' + info.security + '</span>'
                    + '</div>'
                    + '<p style="color:#444;margin-bottom:10px;line-height:1.5;">' + info.what + '</p>'
                    + '<div style="margin-bottom:8px;">'
                    + '<span style="color:#aaa;font-size:0.76em;text-transform:uppercase;letter-spacing:.6px;">Quantum Safe</span><br>'
                    + '<span style="font-weight:600;color:' + (info.quantumSafe?'#28a745':'#dc3545') + ';">'
                    + (info.quantumSafe ? '✓ Yes — quantum-resistant at 256+ bits' : "✗ No — vulnerable to Shor's / Grover's algorithm")
                    + '</span></div>'
                    + '<div style="margin-bottom:' + (info.warn?'8':'0') + 'px;">'
                    + '<span style="color:#aaa;font-size:0.76em;text-transform:uppercase;letter-spacing:.6px;">Use Cases</span><br>'
                    + '<span style="color:#333;">' + info.uses + '</span>'
                    + '</div>';
                if (info.warn) {
                    html += '<div style="margin-top:6px;padding:8px 10px;background:#fff3cd;border-left:3px solid #ffc107;border-radius:4px;color:#856404;font-size:0.82em;">⚠ ' + info.warn + '</div>';
                }
                html += '</div>';
                document.getElementById('presetInfoContent').innerHTML = html;
            }

            // ── Algorithm autocomplete ──────────────────────────────────────────
            function showAlgoSuggestions(val) {
                const list = document.getElementById('algoList');
                if (!val || val.length < 1) { list.style.display = 'none'; return; }
                const lower = val.toLowerCase();
                const matches = KNOWN_ALGOS.filter(a => a.name.toLowerCase().includes(lower)).slice(0, 9);
                if (!matches.length) { list.style.display = 'none'; return; }
                list.innerHTML = matches.map(a =>
                    '<div class="autocomplete-item" onmousedown="selectAlgo(\'' + a.name + '\',' + a.bits + ',\'' + a.type + '\')">'
                    + '<span class="ac-name">' + a.name + '</span>'
                    + '<span class="ac-desc">' + a.desc + '</span>'
                    + '</div>'
                ).join('');
                list.style.display = 'block';
            }

            function selectAlgo(name, bits, type) {
                document.getElementById('algorithm').value = name;
                document.getElementById('algoList').style.display = 'none';
                if (bits) document.getElementById('keyLength').value = bits;
                const typeEl = document.getElementById('assetType');
                if (type && !typeEl.value) typeEl.value = type;
                checkAlgorithm(); checkKeyLength();
            }

            function clearAssetForm() {
                ['assetId','assetName','algorithm','keyLength','expirationDate'].forEach(id => {
                    document.getElementById(id).value = '';
                });
                document.getElementById('assetType').value = '';
                document.getElementById('status').value    = 'active';
                document.getElementById('algoWarning').style.display = 'none';
                document.getElementById('algorithm').style.borderColor = '';
                document.getElementById('keyLengthWarning').style.display = 'none';
                document.getElementById('keyLength').style.borderColor = '';
                document.getElementById('algoList').style.display = 'none';
                document.querySelectorAll('.preset-item').forEach(el => el.classList.remove('selected'));
            }

            function toggleScanPanel() {                const p = document.getElementById('scanPanel');
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
                    const d = data.details || {};
                    const RISK_COLOR = {CRITICAL:'#dc3545',HIGH:'#fd7e14',MEDIUM:'#ffc107',LOW:'#28a745'};
                    const RISK_TEXT  = {CRITICAL:'white',    HIGH:'white',    MEDIUM:'#333',   LOW:'white'};
                    const rc = RISK_COLOR[d.overall_risk] || '#6c757d';
                    const rt = RISK_TEXT[d.overall_risk]  || 'white';

                    // ── Report card ──────────────────────────────────────────
                    let html = `<div style="border:2px solid ${rc};border-radius:8px;padding:16px;margin-bottom:14px;">`;

                    // Header row
                    html += `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">`;
                    html += `<strong style="font-size:1em;">🔍 Scan Report: ${d.hostname || ''}</strong>`;
                    html += `<span style="background:${rc};color:${rt};padding:4px 12px;border-radius:12px;font-size:0.82em;font-weight:600;">${d.overall_risk || 'UNKNOWN'} RISK</span>`;
                    html += `</div>`;

                    // Summary grid
                    html += `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-bottom:12px;">`;
                    const cells = [
                        ['Protocol',    d.tls_version || '—'],
                        ['Cipher Suite', d.cipher ? (d.cipher.length>28 ? d.cipher.substring(0,26)+'…' : d.cipher) : '—'],
                        ['Public Key',   d.pk_type && d.pk_type !== 'Unknown'
                            ? d.pk_type + (d.pk_curve ? ' ('+d.pk_curve+')' : '') + (d.pk_bits ? ', '+d.pk_bits+' bit' : '')
                            : '—'],
                        ['Cert Expires', d.expiry || '—'],
                        ['Days Left',    d.days_left !== null && d.days_left !== undefined
                            ? (d.days_left < 0 ? '⚠ EXPIRED' : d.days_left + ' days')
                            : '—'],
                        ['Issuer',       d.issuer_org || d.issuer_cn || '—'],
                    ];
                    cells.forEach(([label, val]) => {
                        const expired = label === 'Days Left' && d.days_left !== null && d.days_left < 30;
                        html += `<div style="background:#f8f9fa;border-radius:6px;padding:8px 10px;">
                            <div style="font-size:0.75em;color:#888;text-transform:uppercase;letter-spacing:.5px;">${label}</div>
                            <div style="font-size:0.88em;font-weight:600;color:${expired?'#dc3545':'#333'};margin-top:2px;">${val}</div></div>`;
                    });
                    html += `</div>`;

                    // SANs
                    if (d.sans && d.sans.length) {
                        html += `<div style="font-size:0.82em;color:#555;margin-bottom:10px;">
                            <strong>Subject Alt Names:</strong> ${d.sans.join(', ')}${d.sans.length >= 6 ? ' …' : ''}</div>`;
                    }

                    // Findings list
                    if (d.findings && d.findings.length) {
                        html += `<div style="font-size:0.85em;"><strong>Findings</strong><div style="margin-top:6px;">`;
                        d.findings.forEach(f => {
                            const fc = RISK_COLOR[f.severity] || '#6c757d';
                            const ft = RISK_TEXT[f.severity]  || 'white';
                            html += `<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:5px;">
                                <span style="background:${fc};color:${ft};padding:2px 7px;border-radius:10px;font-size:0.78em;white-space:nowrap;flex-shrink:0;">${f.severity}</span>
                                <span style="color:#444;"><strong>${f.category}:</strong> ${f.message}</span></div>`;
                        });
                        html += `</div></div>`;
                    }
                    html += `</div>`;

                    // Asset cards for pre-fill
                    html += `<p style="margin-bottom:8px;font-size:0.9em;color:#555;">Click an asset to pre-fill the form below:</p>`;
                    data.assets.forEach((a, i) => {
                        const statusColors = {deprecated:'#fd7e14',vulnerable:'#dc3545',expired:'#dc3545',active:'#28a745'};
                        const sc = statusColors[a.status] || '#6c757d';
                        html += `<div onclick="prefillAsset(${i})" style="cursor:pointer;padding:10px 14px;border:1px solid #ddd;border-radius:6px;margin-bottom:8px;background:#f9f9f9;" onmouseover="this.style.background='#eef2ff'" onmouseout="this.style.background='#f9f9f9'">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="font-weight:600;">${a.name}</span>
                                <span style="background:${sc};color:white;padding:2px 8px;border-radius:10px;font-size:0.75em;">${a.status}</span>
                            </div>
                            <span style="font-size:0.82em;color:#777;">${a.asset_type} &nbsp;·&nbsp; Algorithm: <strong>${a.algorithm}</strong>`
                            + (a.key_length ? ` &nbsp;·&nbsp; ${a.key_length} bits` : '')
                            + (a.expiration_date ? ` &nbsp;·&nbsp; Expires ${a.expiration_date}` : '')
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
                document.getElementById('assetId').value        = a.id;
                document.getElementById('assetName').value      = a.name;
                document.getElementById('assetType').value      = a.asset_type;
                document.getElementById('algorithm').value      = a.algorithm;
                document.getElementById('keyLength').value      = a.key_length || '';
                document.getElementById('status').value         = a.status || 'active';
                document.getElementById('expirationDate').value = a.expiration_date || '';
                checkAlgorithm(); checkKeyLength();
                document.getElementById('add-asset').querySelector('form').scrollIntoView({behavior:'smooth'});
            }

            window.onload = function() { loadDashboard(); renderPresets(); };
        </script>
    </body>
    </html>
    """
    

    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/summary')
    def api_summary():
        bom = get_user_bom()
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
        bom = get_user_bom()
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
            bom = get_user_bom()
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
            bom = get_user_bom()
            bom.remove_asset(asset_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/audit-log')
    def api_audit_log():
        bom = get_user_bom()
        return jsonify([{
            'timestamp': log.timestamp,
            'action': log.action,
            'asset_id': log.asset_id,
            'asset_name': log.asset_name
        } for log in bom.audit_log[-10:]])
    
    @app.route('/api/validate/detail')
    def api_validate_detail():
        from .validator import CryptoValidator
        bom = get_user_bom()
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
        bom = get_user_bom()
        risk_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        type_counts = {}
        for asset in bom.assets.values():
            risk = asset.risk_level()
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
            type_counts[asset.asset_type] = type_counts.get(asset.asset_type, 0) + 1
        return jsonify({'risk_levels': risk_counts, 'asset_types': type_counts})

    @app.route('/api/validate')
    def api_validate():
        bom = get_user_bom()
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
                    tls_ver     = ssock.version() or 'Unknown'
                    cipher      = ssock.cipher()
                    cipher_name = cipher[0] if cipher else 'Unknown'
                    bits        = cipher[2] if cipher else 0
                    cert_dict   = ssock.getpeercert()
                    cert_der    = ssock.getpeercert(binary_form=True)
        except ssl.SSLError as exc:
            return jsonify({'error': f'TLS error: {exc}'})
        except OSError as exc:
            return jsonify({'error': f'Connection failed: {exc}'})
        except Exception as exc:
            return jsonify({'error': str(exc)})

        def _rdn(seq):
            out = {}
            for rdn in seq:
                for k, v in rdn:
                    out[k] = v.encode('ascii', 'replace').decode('ascii')
            return out

        subject = _rdn(cert_dict.get('subject', ()))
        issuer  = _rdn(cert_dict.get('issuer',  ()))

        not_after  = cert_dict.get('notAfter', '')
        expiry_str = ''
        days_left  = None
        try:
            expiry_dt  = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
            expiry_str = expiry_dt.strftime('%Y-%m-%d')
            days_left  = (expiry_dt - datetime.datetime.utcnow()).days
        except Exception:
            pass

        sans = [v for k, v in cert_dict.get('subjectAltName', ()) if k == 'DNS']
        self_signed = (
            subject.get('commonName') == issuer.get('commonName') and
            subject.get('organizationName', '__a') == issuer.get('organizationName', '__b')
        )

        # ── Deep public-key analysis via `cryptography` library ──────────────
        pk_type  = 'Unknown'
        pk_bits  = 0
        pk_curve = ''
        sig_algo = ''
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa, ed25519, ed448
            cert_obj = x509.load_der_x509_certificate(cert_der)
            pub_key  = cert_obj.public_key()
            try:
                sig_algo = cert_obj.signature_hash_algorithm.name
            except Exception:
                sig_algo = 'Unknown'
            if isinstance(pub_key, rsa.RSAPublicKey):
                pk_type = 'RSA';  pk_bits = pub_key.key_size
            elif isinstance(pub_key, ec.EllipticCurvePublicKey):
                pk_type = 'EC';   pk_bits = pub_key.key_size;  pk_curve = pub_key.curve.name
            elif isinstance(pub_key, dsa.DSAPublicKey):
                pk_type = 'DSA';  pk_bits = pub_key.key_size
            elif isinstance(pub_key, ed25519.Ed25519PublicKey):
                pk_type = 'Ed25519'; pk_bits = 256
            elif isinstance(pub_key, ed448.Ed448PublicKey):
                pk_type = 'Ed448';   pk_bits = 448
        except ImportError:
            pass
        except Exception:
            pass

        # ── Risk findings engine ──────────────────────────────────────────────
        findings     = []
        overall_risk = 'LOW'
        SEVERITY_ORDER = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

        def _bump(current, new):
            return new if SEVERITY_ORDER.index(new) > SEVERITY_ORDER.index(current) else current

        def _finding(severity, category, message):
            findings.append({'severity': severity, 'category': category, 'message': message})
            nonlocal overall_risk
            overall_risk = _bump(overall_risk, severity)

        # Protocol version
        TLS_RISKS = {
            'SSLv2':   ('CRITICAL', 'SSLv2 is completely broken — disable immediately.'),
            'SSLv3':   ('CRITICAL', 'SSLv3 is broken (POODLE). Must be disabled.'),
            'TLSv1':   ('HIGH',     'TLS 1.0 is deprecated (RFC 8996). Upgrade to TLS 1.2+.'),
            'TLSv1.1': ('HIGH',     'TLS 1.1 is deprecated (RFC 8996). Upgrade to TLS 1.2+.'),
            'TLSv1.2': ('MEDIUM',   'TLS 1.2 is acceptable but TLS 1.3 is strongly preferred.'),
            'TLSv1.3': ('LOW',      'TLS 1.3 — current best practice.'),
        }
        if tls_ver in TLS_RISKS:
            _finding(*TLS_RISKS[tls_ver][0:1] + ('Protocol',) + TLS_RISKS[tls_ver][1:2])

        # Cipher suite
        for wc in ['RC4', 'DES', '3DES', 'NULL', 'EXPORT', 'ANON']:
            if wc in cipher_name.upper():
                _finding('CRITICAL', 'Cipher Suite', f'Weak/broken cipher in use: {cipher_name}')
                break
        if 'MD5' in cipher_name.upper():
            _finding('HIGH', 'Cipher Suite', f'MD5-based cipher in use: {cipher_name}')

        # Public key
        if pk_type == 'RSA':
            if pk_bits < 2048:
                _finding('CRITICAL', 'Public Key', f'RSA-{pk_bits} is critically weak — NIST minimum is 2048 bits. Replace immediately.')
            elif pk_bits < 3072:
                _finding('MEDIUM', 'Public Key', f'RSA-{pk_bits} is acceptable until ~2030. Consider RSA-4096 or ECDSA P-256 for longevity.')
            else:
                _finding('LOW', 'Public Key', f'RSA-{pk_bits} meets current best practices.')
            _finding('MEDIUM', 'Quantum Risk', "RSA is vulnerable to Shor's algorithm on quantum computers. Plan migration to post-quantum algorithms (e.g. ML-KEM / CRYSTALS-Kyber).")
        elif pk_type == 'EC':
            weak_curves = {'secp192r1', 'prime192v1', 'secp192k1', 'sect163r2', 'secp112r1'}
            if pk_curve in weak_curves:
                _finding('HIGH', 'Public Key', f'EC curve {pk_curve} is deprecated. Replace with P-256, P-384, or P-521.')
            elif pk_bits < 256:
                _finding('HIGH', 'Public Key', f'EC key is only {pk_bits} bits. Minimum recommended is 256 bits.')
            else:
                label = f'{pk_curve}, {pk_bits}-bit' if pk_curve else f'{pk_bits}-bit'
                _finding('LOW', 'Public Key', f'EC key ({label}) meets current best practices.')
            _finding('MEDIUM', 'Quantum Risk', "ECC is vulnerable to Shor's algorithm. Plan migration to post-quantum algorithms.")
        elif pk_type == 'DSA':
            _finding('HIGH', 'Public Key', 'DSA is deprecated and should be replaced with ECDSA or Ed25519.')
            _finding('MEDIUM', 'Quantum Risk', "DSA is vulnerable to Shor's algorithm. Migrate to post-quantum algorithms.")
        elif pk_type in ('Ed25519', 'Ed448'):
            _finding('LOW', 'Public Key', f'{pk_type} is a modern, efficient algorithm — excellent choice.')
            _finding('MEDIUM', 'Quantum Risk', f'{pk_type} is still vulnerable to quantum attacks. Monitor post-quantum standards.')
        elif pk_type == 'Unknown':
            _finding('MEDIUM', 'Public Key', 'Could not analyse public key type — install the cryptography library for full analysis.')

        # Signature algorithm
        if sig_algo and sig_algo != 'Unknown':
            sl = sig_algo.lower()
            if 'md5' in sl:
                _finding('CRITICAL', 'Signature', f'Certificate signed with MD5 — cryptographically broken.')
            elif 'sha1' in sl:
                _finding('HIGH', 'Signature', f'Certificate signed with SHA-1 — deprecated since 2017.')
            else:
                _finding('LOW', 'Signature', f'Signature algorithm: {sig_algo.upper()} — acceptable.')

        # Certificate expiry
        if days_left is not None:
            if days_left < 0:
                _finding('CRITICAL', 'Expiry', f'Certificate EXPIRED {abs(days_left)} day(s) ago!')
            elif days_left < 14:
                _finding('CRITICAL', 'Expiry', f'Certificate expires in {days_left} day(s) — renew IMMEDIATELY.')
            elif days_left < 30:
                _finding('HIGH', 'Expiry', f'Certificate expires in {days_left} days — renew soon.')
            elif days_left < 90:
                _finding('MEDIUM', 'Expiry', f'Certificate expires in {days_left} days — schedule renewal.')
            else:
                _finding('LOW', 'Expiry', f'Certificate valid for {days_left} more days.')

        # Self-signed
        if self_signed:
            _finding('HIGH', 'Trust', 'Certificate appears self-signed — not trusted by browsers/clients by default.')

        # ── Build BOM assets ──────────────────────────────────────────────────
        safe       = hostname.replace('.', '-').replace('*', 'WILD').upper()
        tls_status = CryptoAsset.auto_detect_status(tls_ver)

        pk_algo_str = f'{pk_type}-{pk_bits}' if pk_type not in ('Unknown', 'Ed25519', 'Ed448') else pk_type
        pk_status   = CryptoAsset.auto_detect_status(pk_algo_str) if pk_type != 'Unknown' else 'active'
        if pk_type == 'DSA':
            pk_status = 'deprecated'

        assets = [
            {
                'id': f'TLS-{safe}', 'name': f'TLS Session on {hostname}',
                'asset_type': 'cipher_suite', 'algorithm': tls_ver,
                'key_length': bits, 'expiration_date': '', 'status': tls_status
            },
            {
                'id': f'CERT-{safe}', 'name': f'Certificate for {hostname}',
                'asset_type': 'certificate', 'algorithm': 'X.509',
                'key_length': 0, 'expiration_date': expiry_str, 'status': 'active'
            },
        ]
        if pk_type != 'Unknown':
            assets.append({
                'id': f'PK-{safe}', 'name': f'Public Key on {hostname}',
                'asset_type': 'key', 'algorithm': pk_algo_str,
                'key_length': pk_bits, 'expiration_date': expiry_str, 'status': pk_status
            })

        return jsonify({
            'assets': assets,
            'details': {
                'hostname':    hostname,
                'tls_version': tls_ver,
                'cipher':      cipher_name,
                'cipher_bits': bits,
                'pk_type':     pk_type,
                'pk_bits':     pk_bits,
                'pk_curve':    pk_curve,
                'sig_algo':    sig_algo,
                'subject_cn':  subject.get('commonName', hostname),
                'issuer_cn':   issuer.get('commonName', ''),
                'issuer_org':  issuer.get('organizationName', ''),
                'expiry':      expiry_str,
                'days_left':   days_left,
                'sans':        sans[:6],
                'self_signed': self_signed,
                'overall_risk': overall_risk,
                'findings':    findings,
            }
        })

    @app.route('/api/export/json')
    def api_export_json():
        bom = get_user_bom()
        tmp = os.path.join(tempfile.gettempdir(), f'cbom_export_{session["sid"]}.json')
        bom.export_json(tmp)
        return send_file(tmp, as_attachment=True, download_name='cbom_export.json')
    
    @app.route('/api/export/csv')
    def api_export_csv():
        bom = get_user_bom()
        tmp = os.path.join(tempfile.gettempdir(), f'cbom_export_{session["sid"]}.csv')
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
