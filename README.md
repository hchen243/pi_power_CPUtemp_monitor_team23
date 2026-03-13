# Raspberry Pi 5 Power Monitor

Real-time power monitoring for Raspberry Pi 5 using hardware PMIC readings via `vcgencmd`.

## Features

- **Hardware-accurate power measurements** from the onboard Power Management IC (PMIC)
- **Real-time monitoring** with 1-second updates
- **Power rail breakdown** showing consumption by voltage rail
- **Energy tracking** in watt-hours (Wh)
- **Live web dashboard** with graphs and statistics

## How It Works

1. **PMIC Reading**: Uses `vcgencmd pmic_read_adc` to read voltage and current from the Pi 5's PMIC
2. **Power Calculation**: Multiplies voltage × current for each power rail to get watts
3. **Energy Integration**: Accumulates power over time using trapezoidal integration
4. **Web Interface**: Flask server serves a real-time dashboard with Chart.js visualization

### Architecture

```
┌─────────────────┐
│  Raspberry Pi 5 │
│      PMIC       │  ← Hardware power monitoring
└────────┬────────┘
         │ vcgencmd pmic_read_adc
         ↓
┌─────────────────┐
│  Python Script  │
│  - Read PMIC    │
│  - Calculate P  │
│  - Track energy │
└────────┬────────┘
         │ Flask API
         ↓
┌─────────────────┐
│  Web Dashboard  │
│  - Live graphs  │
│  - Statistics   │
│  - Rail data    │
└─────────────────┘
```

## Requirements

- Raspberry Pi 5 (required for PMIC access)
- Python 3.7+
- Flask (`pip install flask`)

## Usage

```bash
# Install dependencies
pip install flask

# Run the monitor
python3 power_monitor.py

# Open in browser
http://localhost:5000
```

## API Endpoints

- `GET /` - Web dashboard
- `GET /api/power` - JSON data (power readings, energy, rails)
- `GET /api/reset_energy` - Reset energy counter

## Technical Details

**Sampling Rate**: 1 Hz (1 reading/second)  
**Data Retention**: Last 500 readings (~8 minutes)  
**Energy Calculation**: Trapezoidal integration of power over time  
**Thread Safety**: Locks protect shared data structures

## Files

- `power_monitor.py` - Flask server and monitoring logic
- `index.html` - Web dashboard frontend
