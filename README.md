# 📡 Raspberry Pi 5 Power & Temperature Monitor

### Real‑Time PMIC Power Tracking + CPU Thermal Logging + Interactive Web Dashboard  

**Forked from:** https://github.com/HudsonReynolds2/pi_power_monitor/tree/main  

---

## 🚀 Overview

This project provides a real‑time hardware monitoring dashboard for the **Raspberry Pi 5**, integrating:

- PMIC rail voltage, current, and total power readings  
- CPU temperature logging and visualization  
- Energy consumption tracking (Wh)  
- Flask REST API backend  
- Chart.js interactive web dashboard  
- Live updates at 1 Hz  

It is developed by **Team 23** as part of an **ECE Senior Design** project to support low‑level performance and power analysis of the Raspberry Pi 5 under different workloads.

---

## 🧩 Features

### 🔌 Power Monitoring

*   Reads all PMIC rails using  
    `vcgencmd pmic_read_adc`
*   Computes:
    *   Total system power (W)
    *   Per‑rail power breakdown
    *   Min, max, and average power
    *   Rolling power graph (1-second sampling)

### 🌡 CPU Temperature Monitoring

*   Reads temperature from  
    `/sys/class/thermal/thermal_zone0/temp`  
    (fallback to `vcgencmd measure_temp`)
*   Logs to rolling history buffer
*   Graphs CPU temperature over time
*   Displays live temperature on dashboard

### 📊 Real-Time Web Dashboard

*   Built with **Flask + Chart.js**
*   Updates every 1 second via REST API
*   Two synchronized charts:
    *   Total system power (W)
    *   CPU temperature (°C)
*   Responsive UI styled for team documentation needs

### 🧮 Energy Tracking

*   Integrates power values using trapezoidal method
*   Displays total energy consumption (Wh)

***

## 🛠 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Install dependencies

```bash
pip3 install flask
```

### 3. Run the monitoring server

```bash
python3 power_monitor.py
```

### 4. Open the dashboard

Use a browser and navigate to:

    http://<raspberry-pi-ip>:5000

***

## 📡 API Endpoints

### `GET /api/power`

Returns:

```json
{
  "power_readings": [
    { "timestamp": "12:00:01", "power": 3.42, "cpu_temp": 48.1 }
  ],
  "cpu_temp_readings": [
    { "timestamp": "12:00:01", "temp": 48.1 }
  ],
  "total_energy_wh": 0.1234,
  "rails": {
    "vcore": { "voltage": 0.89, "current": 1.12, "power": 0.9968 }
  }
}
```

### `GET /api/reset_energy`

Resets the accumulated energy counter.

***

## 🧪 Integration Testing Summary

Key validated results include:

*   ✔ PMIC power readings update reliably at 1 Hz
*   ✔ CPU temperature logging integrated into backend and visualized in chart
*   ✔ Both charts refresh smoothly with no UI stutter
*   ✔ Dashboard handles PMIC read failures gracefully
*   ✔ Rails breakdown matches expected values
*   ✔ No crashes during 30‑minute stress test

Full test results documented in:  
**`Team23_Integration_Testing_Results.docx`**

***

## 📁 Project Structure

    project/
    │── power_monitor.py        # Backend: PMIC + Temp monitoring + API
    │── index.html              # Frontend dashboard (Chart.js)
    │── static/                 # (Optional) Additional JS/CSS assets
    │── Team23_Integration_Testing_Results.docx
    │── README.md

***

## 🧱 Hardware Requirements

*   Raspberry Pi 5 (8 GB recommended)
*   NVMe storage (optional but supported)
*   PCIe adapter or HAT
*   PoE+ HAT
*   PoE+ switch or injector
*   Cooling recommended for sustained tests

***

## 🤝 Team Workflow

We use:

*   **GitHub** for version control
*   **VS Code** for development
*   **Azure for Students** for documentation and cloud testing
*   **Microsoft Teams** for collaboration & communication

Feature branches and pull requests are recommended for:

*   Adding rail visualization
*   Adding overlay charts
*   Adding alerts for over-current or over-temperature
*   Expanding API endpoints

***

## 📌 Future Enhancements

*   Overlay CPU temperature on power chart (dual‑axis)
*   CSV/Excel export of logs
*   Long-term database logging via SQLite or Azure
*   Fan control integration
*   Thermal throttling detection

***

## 📝 License

MIT License.  
Free for educational and research use.

***

## 👥 Authors

Team 23 — ECE Senior Design  
Raspberry Pi 5 Hardware Analysis & Monitoring

***

