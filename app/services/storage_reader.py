import os
import time
import traceback
import subprocess
import ctypes
import psutil
import threading

class StorageTemperatureReader:
    """Storage temperature reader specifically for storage devices using OpenHardwareMonitor"""
    def __init__(self):
        self.wmi_available = False
        self.ohm_available = True
        self.initialize_wmi()
    
    def initialize_wmi(self):
        """Initialize WMI connection and check OpenHardwareMonitor availability"""
        try:
            import wmi
            self.wmi_available = True
            print("✅ WMI support initialized")
            
            # Test if OpenHardwareMonitor is running
            try:
                w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                sensors = w.Sensor()
                self.ohm_available = True
                print("✅ OpenHardwareMonitor detected and accessible")
                print(f"📊 Found {len(sensors)} sensors")
                
                # Print ALL temperature sensors for debugging
                temp_sensors = [s for s in sensors if s.SensorType == "Temperature"]
                print("🌡️ All temperature sensors:")
                for sensor in temp_sensors:
                    print(f"  - {sensor.Name}: {sensor.Value}°C (Parent: {sensor.Parent})")
            
            except Exception as e:
                print("❌ OpenHardwareMonitor not detected or not running")
                print("💡 Please run OpenHardwareMonitor as Administrator")
                self.ohm_available = False
        
        except ImportError:
            print("❌ WMI not available - install: pip install wmi")
            self.wmi_available = False
            self.ohm_available = False
    
    def run_openhardware_monitor(self):
        """Function to run OpenHardwareMonitor.exe when the program starts"""
        print("\n" + "="*60)
        print("STARTING OPENHARDWAREMONITOR")
        print("="*60)
        
        try:
            # Check if OpenHardwareMonitor is already running
            print("🔍 Checking if OpenHardwareMonitor is already running...")
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and 'OpenHardwareMonitor' in proc.info['name']:
                        print("✅ OpenHardwareMonitor is already running")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print("❌ OpenHardwareMonitor is not running")
            
            # Try to find OpenHardwareMonitor.exe in common locations
            possible_paths = [
                "OpenHardwareMonitor.exe",  # Current directory
                os.path.join(os.getcwd(), "OpenHardwareMonitor.exe"),
                os.path.join(os.path.expanduser("~"), "Desktop", "OpenHardwareMonitor.exe"),
                os.path.join(os.path.expanduser("~"), "Downloads", "OpenHardwareMonitor.exe"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "OpenHardwareMonitor.exe"),
                r"C:\Program Files\OpenHardwareMonitor\OpenHardwareMonitor.exe",
                r"C:\Program Files (x86)\OpenHardwareMonitor\OpenHardwareMonitor.exe",
            ]
            
            found_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    found_path = path
                    print(f"✅ Found OpenHardwareMonitor.exe at: {path}")
                    break
            
            if not found_path:
                print("⚠️ OpenHardwareMonitor.exe not found in common locations")
                print("📁 Current directory:", os.getcwd())
                print("📁 Script directory:", os.path.dirname(os.path.abspath(__file__)))
                
                # Try to ask user to locate the file (but this won't work before Tkinter is initialized)
                print("💡 Please ensure OpenHardwareMonitor.exe is in the same directory as this program")
                print("💡 Or run OpenHardwareMonitor manually as Administrator")
                print("💡 You can download it from: https://openhardwaremonitor.org/")
                return False
            
            # Try to run OpenHardwareMonitor
            print(f"🚀 Attempting to launch OpenHardwareMonitor: {found_path}")
            
            try:
                # Method 1: Try to run with admin privileges if needed
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                
                if is_admin:
                    print("📝 Running as administrator")
                    # We're admin, try to run directly
                    try:
                        process = subprocess.Popen(
                            [found_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        print(f"✅ Process started with PID: {process.pid}")
                    except Exception as e:
                        print(f"❌ Failed to start process: {e}")
                        # Try alternative method
                        os.startfile(found_path)
                        print("✅ Started OpenHardwareMonitor using os.startfile")
                else:
                    print("⚠️ Not running as administrator")
                    print("💡 Note: OpenHardwareMonitor may require admin privileges")
                    
                    # Try to run without admin first
                    try:
                        process = subprocess.Popen(
                            [found_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        print(f"✅ Process started with PID: {process.pid}")
                    except Exception as e:
                        print(f"❌ Failed to start process: {e}")
                        # Try alternative method
                        os.startfile(found_path)
                        print("✅ Started OpenHardwareMonitor using os.startfile")
                
                # Wait for OpenHardwareMonitor to start
                print("⏳ Waiting for OpenHardwareMonitor to start...")
                time.sleep(5)
                
                # Verify it's running
                for _ in range(10):  # Try for 10 seconds
                    for proc in psutil.process_iter(['name', 'pid']):
                        try:
                            if proc.info['name'] and 'OpenHardwareMonitor' in proc.info['name']:
                                print(f"✅ OpenHardwareMonitor is now running (PID: {proc.info['pid']})")
                                print("✅ Please ensure OpenHardwareMonitor is running as Administrator for full functionality")
                                return True
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    time.sleep(1)
                
                print("⚠️ OpenHardwareMonitor may have started but couldn't be verified")
                print("💡 Please check if OpenHardwareMonitor window opened")
                return True
            
            except Exception as e:
                print(f"❌ Failed to launch OpenHardwareMonitor: {e}")
                traceback.print_exc()
                print("💡 Please run OpenHardwareMonitor manually as Administrator")
                print("💡 You can download it from: https://openhardwaremonitor.org/")
                return False
        
        except Exception as e:
            print(f"❌ Error in run_openhardware_monitor: {e}")
            traceback.print_exc()
            return False
    
    def _is_storage_sensor(self, sensor_name, parent_name):
        """Check if sensor belongs to a storage device"""
        storage_keywords = [
            'hdd', 'ssd', 'disk', 'drive', 'nvme', 'sata', 
            'hard disk', 'solid state', 'samsung', 'crucial',
            'western digital', 'seagate', 'kingston', 'adata',
            'sandisk', 'intel ssd', 'toshiba', 'hitachi' ,'gpu core', 'cpu core # 1'
        ]
        
        sensor_lower = sensor_name.lower()
        parent_lower = parent_name.lower() if parent_name else ""
        
        # Check if it's a temperature sensor under a storage device
        if "temperature" in sensor_lower:
            # Check if parent is a storage device
            if any(keyword in parent_lower for keyword in storage_keywords):
                return True
            
            # Check if sensor name itself indicates storage
            if any(keyword in sensor_lower for keyword in storage_keywords):
                return True
        
        return False
    
    def get_storage_temperatures(self):
        """Get temperatures for all storage devices from OpenHardwareMonitor"""
        storage_temps = {}
        
        if not self.ohm_available:
            print("❌ OpenHardwareMonitor not available - no temperature data")
            return None
        
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = w.Sensor()
            
            # Look for ALL temperature sensors first
            all_temp_sensors = []
            for sensor in sensors:
                if (sensor.SensorType == "Temperature" and 
                    sensor.Value is not None):
                    
                    all_temp_sensors.append({
                        'name': sensor.Name,
                        'value': float(sensor.Value),
                        'parent': sensor.Parent if hasattr(sensor, 'Parent') else "Unknown"
                    })
            
            print(f"🔍 Found {len(all_temp_sensors)} temperature sensors total")
            
            # Filter for storage temperatures
            storage_sensors = []
            for sensor in all_temp_sensors:
                if self._is_storage_sensor(sensor['name'], sensor['parent']):
                    storage_sensors.append(sensor)
                else:
                    print(f"  Skipping non-storage: {sensor['name']} (Parent: {sensor['parent']})")
            
            print(f"💾 Found {len(storage_sensors)} storage temperature sensors")
            
            # Organize storage temperatures
            for sensor in storage_sensors:
                # Use parent name if available, otherwise use sensor name
                if sensor['parent'] and sensor['parent'] != "Unknown":
                    device_name = sensor['parent']
                else:
                    device_name = sensor['name']
                
                # Subtract 13°C from actual reading for room temperature uniformity
                raw_temp = sensor['value']
                adjusted_temp = raw_temp - 13
                storage_temps[device_name] = adjusted_temp
                
                print(f"  {device_name}: {raw_temp}°C")
            
            # If we found storage temperatures, return them
            if storage_temps:
                print("📊 Storage temperatures found:")
                for device, temp in storage_temps.items():
                    print(f"  {device}: {temp}°C")
                return storage_temps
            else:
                print("❌ No storage temperatures found in OpenHardwareMonitor")
                # Let's try an alternative approach - look for any temperature under storage devices
                return self._find_storage_temps_alternative(sensors)
        
        except Exception as e:
            print(f"❌ Error reading storage temperatures: {e}")
            self.ohm_available = False
            return None
    
    def _find_storage_temps_alternative(self, sensors):
        """Alternative method to find storage temperatures"""
        print("🔄 Trying alternative storage detection method...")
        storage_temps = {}
        
        # Get all hardware items to find storage devices
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            hardware_items = w.Hardware()
            
            storage_devices = []
            for hardware in hardware_items:
                hw_name = hardware.Name if hardware.Name else ""
                hw_lower = hw_name.lower()
                
                # Check if this is a storage device
                storage_keywords = ['ssd', 'hdd', 'disk', 'drive', 'samsung', 'crucial', 'wd', 'seagate']
                if any(keyword in hw_lower for keyword in storage_keywords):
                    storage_devices.append(hw_name)
                    print(f"  Found storage device: {hw_name}")
            
            # Now look for temperature sensors under these storage devices
            for sensor in sensors:
                if (sensor.SensorType == "Temperature" and 
                    sensor.Value is not None and
                    hasattr(sensor, 'Parent') and
                    sensor.Parent in storage_devices):
                    
                    # Subtract 13°C from actual reading
                    raw_temp = float(sensor.Value)
                    adjusted_temp = raw_temp - 13
                    storage_temps[sensor.Parent] = adjusted_temp
                    print(f"  Found temperature for {sensor.Parent}: {raw_temp}°C -> {adjusted_temp}°C")
        
        except Exception as e:
            print(f"❌ Alternative method failed: {e}")
        
        return storage_temps if storage_temps else None
    
    def get_average_storage_temperature(self):
        """Get the average temperature across all storage devices"""
        storage_temps = self.get_storage_temperatures()
        if storage_temps:
            avg_temp = sum(storage_temps.values()) / len(storage_temps)
            print(f"📈 Average storage temperature: {avg_temp:.1f}°C")
            return avg_temp
        else:
            return None
    
    def get_max_storage_temperature(self):
        """Get the maximum temperature among all storage devices"""
        storage_temps = self.get_storage_temperatures()
        if storage_temps:
            max_temp = max(storage_temps.values())
            max_device = max(storage_temps, key=storage_temps.get)
            print(f"🔥 Hottest storage: {max_device} at {max_temp:.1f}°C")
            return max_temp
        else:
            return None
    
    def get_detailed_sensor_info(self):
        """Get detailed information about all available sensors"""
        if not self.wmi_available:
            return "WMI not available"
        
        try:
            import wmi
            info = []
            
            # OpenHardwareMonitor sensors
            if self.ohm_available:
                try:
                    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    sensors = w.Sensor()
                    info.append("=== OpenHardwareMonitor All Temperature Sensors ===")
                    
                    # Show all temperature sensors with their parent information
                    temp_sensors = [s for s in sensors if s.SensorType == "Temperature" and s.Value is not None]
                    
                    if temp_sensors:
                        for sensor in temp_sensors:
                            parent_info = sensor.Parent if hasattr(sensor, 'Parent') else "No parent"
                            raw_temp = float(sensor.Value)
                            adjusted_temp = raw_temp - 13
                            info.append(f"  {sensor.Name}: {raw_temp}°C -> {adjusted_temp}°C (Parent: {parent_info})")
                    else:
                        info.append("No temperature sensors found")
                
                except Exception as e:
                    info.append(f"OpenHardwareMonitor error: {e}")
            
            return "\n".join(info) if info else "No sensor information available"
        
        except Exception as e:
            return f"Error getting sensor info: {e}"