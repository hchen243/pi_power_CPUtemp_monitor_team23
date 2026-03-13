#!/usr/bin/env python3
"""Raspberry Pi 5 Power Monitor - Real-time PMIC monitoring via vcgencmd"""

import time
import json
import re
import subprocess
import os
from datetime import datetime
from collections import deque
from flask import Flask, send_file, jsonify
from threading import Thread, Lock

app = Flask(__name__)

power_data = deque(maxlen=500)
data_lock = Lock()

total_energy_wh = 0.0
last_power_reading = 0.0
last_reading_time = time.time()
energy_lock = Lock()

rail_data = {}
rail_lock = Lock()


# Added on 3/13/2026: store CPU temperature history
cpu_temp_data = deque(maxlen=500)
cpu_temp_lock = Lock()


# Modified on 3/11/2026
def get_cpu_temperature():
    """
    Returns CPU temperature in Celsius as a float.
    """
    temp_file = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(temp_file, "r") as f:
            temp_str = f.readline().strip()
        temp_c = int(temp_str) / 1000.0
        return temp_c
    except (FileNotFoundError, ValueError, OSError):
        # Fallback: try vcgencmd if available
        try:
            res = os.popen("vcgencmd measure_temp").read().strip()
            # Expected format: temp=49.2'C
            if res.startswith("temp="):
                temp_val = res.split("=")[1].split("'")[0]
                return float(temp_val)
        except Exception:
            pass
        return None


def read_pmic_power():
    """Read power from Pi 5 PMIC. Returns (total_power_watts, rails_dict)"""
    try:
        result = subprocess.run(['vcgencmd', 'pmic_read_adc'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode != 0:
            raise Exception(f"vcgencmd failed: {result.stderr}")
        
        currents, voltages = {}, {}
        for line in result.stdout.split('\n'):
            if curr := re.search(r'(.+?)\s+current\(\d+\)=([\d.]+)A', line):
                currents[curr.group(1).strip()] = float(curr.group(2))
            if volt := re.search(r'(.+?)\s+volt\(\d+\)=([\d.]+)V', line):
                voltages[volt.group(1).strip()] = float(volt.group(2))
        
        rails, total_power = {}, 0.0
        for curr_name, current in currents.items():
            base = curr_name.replace('_A', '')
            if (volt_name := base + '_V') in voltages:
                voltage = voltages[volt_name]
                power = voltage * current
                total_power += power
                rails[base] = {'voltage': voltage, 'current': current, 'power': power}
        
        return total_power, rails
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        raise Exception(f"Error reading PMIC: {e}")

def monitor_power():
    """Background thread for continuous monitoring"""
    global total_energy_wh, last_power_reading, last_reading_time
    
    while True:
        try:
            power_w, rails = read_pmic_power()
            cpu_temp = get_cpu_temperature()  # added on 3/13/2026
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            current_time = time.time()
            time_delta_hours = (current_time - last_reading_time) / 3600
            
            with energy_lock:
                energy_increment = ((last_power_reading + power_w) / 2) * time_delta_hours
                total_energy_wh += energy_increment
                last_power_reading = power_w
                last_reading_time = current_time
            
            #with data_lock:
                #power_data.append({'timestamp': timestamp, 'power': round(power_w, 3)})
            
# Store power (and optionally latest CPU temp in same entry)
            with data_lock:
                entry = {
                    'timestamp': timestamp,
                    'power': round(power_w, 3),
                }
                if cpu_temp is not None:
                    entry['cpu_temp'] = round(cpu_temp, 2)
                power_data.append(entry)
            
            # Store separate CPU temp history as well
            if cpu_temp is not None:
                with cpu_temp_lock:
                    cpu_temp_data.append({
                        'timestamp': timestamp,
                        'temp': round(cpu_temp, 2)
                    })

            with rail_lock:
                global rail_data
                rail_data = rails
        except Exception as e:
            print(f"Error reading power: {e}")
        
        time.sleep(1)

@app.route('/')
def index():
    #cpu_temp = get_cpu_temperature()
    return send_file('index.html')
    #return render_template("index.html", cpu_temp=cpu_temp) # added 3/11/2026
    

@app.route('/api/power')
def get_power_data():
    with data_lock:
        readings = list(power_data)
    with energy_lock:
        energy = total_energy_wh
    with rail_lock:
        rails = dict(rail_data)
    with cpu_temp_lock:# added on 3/13/2026
        temps = list(cpu_temp_data)

    return jsonify({'power_readings': readings, 'total_energy_wh': energy, 'rails': rails,'cpu_temp_readings': temps})

@app.route('/api/reset_energy')
def reset_energy():
    global total_energy_wh
    with energy_lock:
        total_energy_wh = 0.0
    return jsonify({'status': 'ok', 'total_energy_wh': 0.0})

# added on 3/12/2026
@app.route('/api/cpu-temp')
def get_cpu_temp():
    temp_c = get_cpu_temperature()
    if temp_c is None:
        return jsonify({
            'status': 'error',
            'message': 'Temperature unavailable'
        }), 500
    return jsonify({
        'status': 'ok',
        'cpu_temp_c': temp_c
    })

def main():
    global last_reading_time
    last_reading_time = time.time()
    
    print("=" * 70)
    print("RASPBERRY PI 5 POWER MONITOR")
    print("=" * 70)
    
    try:
        test_power, test_rails = read_pmic_power()
        print(f"\n✓ PMIC connected - Total Power: {test_power:.3f}W\n")
        print("Power breakdown by rail:")
        for rail, vals in sorted(test_rails.items(), key=lambda x: x[1]['power'], reverse=True):
            print(f"  {rail:15s}: {vals['power']:6.3f}W ({vals['voltage']:5.2f}V × {vals['current']:6.3f}A)")
        
        print("\n" + "=" * 70)
        print("🌐 Web Interface: http://localhost:5000")
        print("Press Ctrl+C to stop\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nEnsure you're on Raspberry Pi 5 with vcgencmd available")
        return
    
    Thread(target=monitor_power, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
