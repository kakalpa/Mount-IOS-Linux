"""
iOS Mount GUI - Python Backend Server
Provides REST API for the Electron frontend
"""

import json
import subprocess
import os
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Setup directories
APP_DIR = Path.home() / ".ios_mount_gui"
APP_DIR.mkdir(exist_ok=True)
LOG_FILE = APP_DIR / "operation_log.json"

def run_command(command, timeout=30):
    """Execute a shell command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out",
            "code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "code": -1
        }

def log_operation(operation, status, details=""):
    """Log operation to file"""
    try:
        logs = []
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "status": status,
            "details": details
        }
        logs.append(log_entry)
        
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Failed to log operation: {e}")

# API Routes
@app.route('/api/check-device', methods=['POST'])
def check_device():
    """Check if device is paired"""
    result = run_command("idevicepair validate")
    status = "SUCCESS" if result["success"] else "FAILED"
    log_operation("Check Device", status, result["stdout"][:100])
    return jsonify(result)

@app.route('/api/pair-device', methods=['POST'])
def pair_device():
    """Pair with device"""
    result = run_command("idevicepair pair")
    status = "SUCCESS" if result["success"] else "FAILED"
    log_operation("Pair Device", status, result["stdout"][:100])
    return jsonify(result)

@app.route('/api/mount', methods=['POST'])
def mount_device():
    """Mount device"""
    data = request.json
    mount_point = data.get('mount_point', os.path.expanduser('~/iPhone'))
    
    os.makedirs(mount_point, exist_ok=True)
    result = run_command(f"ifuse {mount_point}")
    status = "SUCCESS" if result["success"] else "FAILED"
    log_operation("Mount Device", status, result["stdout"][:100])
    return jsonify(result)

@app.route('/api/unmount', methods=['POST'])
def unmount_device():
    """Unmount device"""
    data = request.json
    mount_point = data.get('mount_point', os.path.expanduser('~/iPhone'))
    
    result = run_command(f"fusermount -u {mount_point}")
    status = "SUCCESS" if result["success"] else "FAILED"
    log_operation("Unmount Device", status, result["stdout"][:100])
    return jsonify(result)

@app.route('/api/one-click-mount', methods=['POST'])
def one_click_mount():
    """Validate, pair, and mount in one operation"""
    data = request.json
    mount_point = data.get('mount_point', os.path.expanduser('~/iPhone'))
    
    output = []
    os.makedirs(mount_point, exist_ok=True)
    
    # Validate
    result = run_command("idevicepair validate")
    output.append({"step": "validate", "result": result})
    
    # Pair if needed
    if not result["success"]:
        result = run_command("idevicepair pair")
        output.append({"step": "pair", "result": result})
    
    # Mount
    result = run_command(f"ifuse {mount_point}")
    output.append({"step": "mount", "result": result})
    
    success = output[-1]["result"]["success"]
    status = "SUCCESS" if success else "FAILED"
    log_operation("One-Click Mount", status)
    
    return jsonify({"success": success, "steps": output})

@app.route('/api/device-info', methods=['GET'])
def get_device_info():
    """Get device information"""
    info = {}
    
    # Get device UDID
    result = run_command("idevice_id -l")
    if result["success"] and result["stdout"].strip():
        device_id = result["stdout"].strip().split('\n')[0]
        info['udid'] = device_id
        
        # Get device name
        result = run_command(f"idevicename -u {device_id}")
        if result["success"]:
            info['name'] = result["stdout"].strip()
        
        # Get device class
        result = run_command(f"ideviceinfo -u {device_id} -k DeviceClass")
        if result["success"]:
            info['class'] = result["stdout"].strip()
        
        # Get product type
        result = run_command(f"ideviceinfo -u {device_id} -k ProductType")
        if result["success"]:
            info['product_type'] = result["stdout"].strip()
        
        # Get iOS version
        result = run_command(f"ideviceinfo -u {device_id} -k ProductVersion")
        if result["success"]:
            info['ios_version'] = result["stdout"].strip()
        
        # Get storage
        result = run_command(f"ideviceinfo -u {device_id} -k TotalDiskCapacity")
        if result["success"]:
            try:
                total = int(result["stdout"].strip()) / (1024**3)
                info['total_storage'] = f"{total:.2f} GB"
            except:
                pass
        
        result = run_command(f"ideviceinfo -u {device_id} -k FreeDiskSpace")
        if result["success"]:
            try:
                free = int(result["stdout"].strip()) / (1024**3)
                info['free_storage'] = f"{free:.2f} GB"
            except:
                pass
    else:
        info['error'] = 'No device found'
    
    log_operation("Get Device Info", "SUCCESS")
    return jsonify(info)

@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    """Open mounted folder"""
    data = request.json
    mount_point = data.get('mount_point', os.path.expanduser('~/iPhone'))
    
    if os.path.ismount(mount_point):
        result = run_command(f"xdg-open {mount_point}")
        log_operation("Open Folder", "SUCCESS" if result["success"] else "FAILED")
        return jsonify(result)
    else:
        return jsonify({"success": False, "stderr": "Device not mounted"}), 400

@app.route('/api/is-mounted', methods=['POST'])
def is_mounted():
    """Check if device is mounted"""
    data = request.json
    mount_point = data.get('mount_point', os.path.expanduser('~/iPhone'))
    
    mounted = os.path.ismount(mount_point)
    return jsonify({"mounted": mounted})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get operation logs"""
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
            return jsonify(logs)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return jsonify([])

@app.route('/api/logs', methods=['DELETE'])
def clear_logs():
    """Clear operation logs"""
    try:
        LOG_FILE.unlink(missing_ok=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/api/list-apps', methods=['GET'])
def list_apps():
    """List available apps on the device"""
    result = run_command("ifuse --list-apps")
    if result["success"]:
        apps = result["stdout"].strip().split('\n')
        apps = [app.strip() for app in apps if app.strip()]
        return jsonify({"success": True, "apps": apps})
    else:
        return jsonify({"success": False, "error": result["stderr"]}), 400

@app.route('/api/mount-app', methods=['POST'])
def mount_app():
    """Mount a specific app's documents folder"""
    data = request.json
    bundle_id = data.get('bundle_id')
    mount_point = data.get('mount_point', os.path.expanduser('~/iPhone_Apps/app'))
    
    os.makedirs(mount_point, exist_ok=True)
    result = run_command(f"ifuse --documents {bundle_id} {mount_point}")
    status = "SUCCESS" if result["success"] else "FAILED"
    log_operation(f"Mount App {bundle_id}", status, result["stdout"][:100])
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
