from flask import Flask, jsonify
from flask_cors import CORS
import irsdk, math

app = Flask(__name__)

class State:
    ir_connected = False
    last_car_setup_tick = -1

def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # Reset your State variables
        state.last_car_setup_tick = -1
        # Shut down irsdk library (clearing all internal variables)
        ir.shutdown()
        print('irsdk disconnected')
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        print('irsdk connected')

@app.route('/api/sessioninfo', methods=['GET'])
def get_session_info():
    check_iracing()
    
    if state.ir_connected:
        session_info = ir['SessionInfo']  # Fetch session info from iRacing SDK
        speed = ir['Speed']
        return jsonify(session_info, round(speed,1))  # Convert to JSON and return it
    else:
        return jsonify({"error": "iRacing is not connected"}), 503

@app.route('/api/fuel', methods=['GET'])
def get_fuel():
    check_iracing()
    
    if state.ir_connected:
        fuel = ir['FuelLevel']
        return jsonify(fuel)
    else:
        return jsonify({"error": "iRacing is not connected"}), 503

@app.route('/api/replay', methods=['GET'])
def get_replay_info():
    check_iracing()
    
    if state.ir_connected:
        replay_info = ir['ReplayFrameNum']
        driver_info = ir['DriverInfo']
        d = ir['LapBestLap']
    else:
        return jsonify({"error": "iRacing is not connected"}), 503
    return jsonify(replay_info, driver_info, d)

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    check_iracing()
    if state.ir_connected:
        ir.freeze_var_buffer_latest()
        speed = ir['Speed'] # Speed is in m/s, should be converted in Frontend
        throttle = ir['Throttle']*100
        clutch = 100 - ir['Clutch']*100 # Somehow the clutch value is inverted
        clutchRaw = 100 -  ir['ClutchRaw']*100
        brake = ir['Brake']*100
        angle = ir['SteeringWheelAngle'] * (180/math.pi)
        gear = ir['Gear']
        json = {
            "speed": speed,
            "throttle": round(throttle,1),
            "brake": round(brake,1),
            "clutch": round(clutch,1),
            "clutchRaw": round(clutchRaw,1),
            "wheelangle": round(angle,1),
            "gear": gear
        }
        return jsonify(json)
    else:
        return jsonify({"error": "iRacing is not connected"}), 503

if __name__ == '__main__':
    ir = irsdk.IRSDK()
    state = State()
    
    CORS(app)
    app.run(host='localhost', port=3001, debug=True)
