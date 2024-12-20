import time
from rtlsdr import RtlSdr
from skyfield.api import load, Topos
from datetime import datetime

# Observer's location
observer = Topos('60.3913 N', '5.3221 E')  # Bergen, Norway

# Load satellite TLE data
satellites = load.tle_file('https://celestrak.com/NORAD/elements/weather.txt')
satellite = {sat.name: sat for sat in satellites}['NOAA 18']

# Initialize SDR
sdr = RtlSdr()
sdr.sample_rate = 2.048e6  # Adjust as per satellite frequency
sdr.center_freq = 137.9125e6  # NOAA 18 frequency
sdr.gain = 50

# Continuous reception and decoding
try:
    while True:
        # Get satellite position
        ts = load.timescale()
        t = ts.now()
        difference = satellite - observer
        topocentric = difference.at(t)
        alt, az, _ = topocentric.altaz()

        # Check if satellite is above horizon
        if alt.degrees > 0:
            print(f"Satellite visible. Altitude: {alt.degrees:.2f}°, Azimuth: {az.degrees:.2f}°")

            # Capture signal from SDR
            samples = sdr.read_samples(256*1024)  # Adjust size based on performance

            # Decode and process (example only - decoding depends on satellite signal format)
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            with open(f"satellite_image_{timestamp}.raw", 'wb') as f:
                f.write(samples.tobytes())
            print(f"Image captured at {timestamp}")

        else:
            print("Satellite not visible.")

        time.sleep(5)  # Wait 5 seconds before next capture

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    sdr.close()
