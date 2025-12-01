#!/usr/bin/env python3
"""
Air Quality Data Extractor
Extracts latest real-time sensor data from Awair Omni and Kaiterra Sensedge Mini devices.
Outputs consolidated data to a single CSV file.
"""

import requests
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict, Any, Optional


class AwairDataExtractor:
    """Handles data extraction from Awair Omni devices via Enterprise Dashboard API."""
    
    BASE_URL = "https://developer-apis.awair.is/v1/users/self/devices"
    RATE_LIMIT_DELAY = 6  # seconds (10 requests per minute = 1 request per 6 seconds)
    
    def __init__(self, api_key: str):
        """
        Initialize Awair data extractor.
        
        Args:
            api_key: Awair API key for authentication
        """
        self.api_key = api_key
        self.headers = {"x-api-key": api_key}
    
    def get_device_data(self, device_id: str) -> Dict[str, Any]:
        """
        Retrieve latest air quality data for a specific Awair device.
        
        Args:
            device_id: The unique identifier for the Awair device
            
        Returns:
            Dictionary containing parsed sensor data or error information
        """
        result = {
            "Source": "Awair",
            "Device_ID": device_id,
            "Timestamp_UTC": None,
            "Error": None
        }
        
        try:
            # Awair API endpoint for latest data
            url = f"{self.BASE_URL}/omni/{device_id}/air-data/latest"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse timestamp
            if "timestamp" in data:
                result["Timestamp_UTC"] = data["timestamp"]
            
            # Parse sensor data from nested sensors array
            if "sensors" in data:
                for sensor in data["sensors"]:
                    comp = sensor.get("comp", "unknown")
                    value = sensor.get("value")
                    
                    # Map sensor components to readable column names
                    sensor_mapping = {
                        "temp": "Temperature_°C",
                        "humid": "Humidity_%",
                        "co2": "CO2_ppm",
                        "voc": "VOC_ppb",
                        "pm25": "PM2.5_µg/m³",
                        "pm10": "PM10_µg/m³"
                    }
                    
                    column_name = sensor_mapping.get(comp, f"{comp}_value")
                    result[column_name] = value
            
            # Parse score if present
            if "score" in data:
                result["Awair_Score"] = data["score"]
                
        except requests.exceptions.HTTPError as e:
            result["Error"] = f"HTTP Error: {e.response.status_code} - {e.response.reason}"
        except requests.exceptions.RequestException as e:
            result["Error"] = f"Request Error: {str(e)}"
        except Exception as e:
            result["Error"] = f"Parsing Error: {str(e)}"
        
        return result
    
    def get_all_devices_data(self, device_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve data for all specified Awair devices with rate limiting.
        
        Args:
            device_ids: List of Awair device identifiers
            
        Returns:
            List of dictionaries containing device data
        """
        all_data = []
        
        for i, device_id in enumerate(device_ids):
            print(f"Fetching Awair device {i+1}/{len(device_ids)}: {device_id}")
            device_data = self.get_device_data(device_id)
            all_data.append(device_data)
            
            # Rate limiting: sleep after each request (except the last one)
            if i < len(device_ids) - 1:
                time.sleep(self.RATE_LIMIT_DELAY)
        
        return all_data


class KaiterraDataExtractor:
    """Handles data extraction from Kaiterra Sensedge Mini devices via Public API."""
    
    BASE_URL = "https://api.kaiterra.com/v1/lasereggs"
    
    def __init__(self, api_key: str):
        """
        Initialize Kaiterra data extractor.
        
        Args:
            api_key: Kaiterra API key for authentication
        """
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}
    
    def get_device_data(self, device_id: str) -> Dict[str, Any]:
        """
        Retrieve latest air quality data for a specific Kaiterra device.
        
        Args:
            device_id: The unique identifier for the Kaiterra device
            
        Returns:
            Dictionary containing parsed sensor data or error information
        """
        result = {
            "Source": "Kaiterra",
            "Device_ID": device_id,
            "Timestamp_UTC": None,
            "Error": None
        }
        
        try:
            # Kaiterra API endpoint for latest data
            url = f"{self.BASE_URL}/{device_id}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse timestamp
            if "info" in data and "aqi" in data["info"] and "ts" in data["info"]["aqi"]:
                result["Timestamp_UTC"] = data["info"]["aqi"]["ts"]
            
            # Parse highly nested sensor data
            if "latest" in data and "data" in data["latest"]:
                sensor_data = data["latest"]["data"]
                
                # Extract each sensor reading with its unit
                for sensor_key, sensor_info in sensor_data.items():
                    if isinstance(sensor_info, dict):
                        value = sensor_info.get("value")
                        unit = sensor_info.get("units", "")
                        
                        # Create column name with unit
                        sensor_mapping = {
                            "pm25": "PM2.5",
                            "pm10": "PM10",
                            "tvoc": "TVOC",
                            "temp": "Temperature",
                            "humid": "Humidity",
                            "co2": "CO2"
                        }
                        
                        base_name = sensor_mapping.get(sensor_key, sensor_key.upper())
                        column_name = f"{base_name}_{unit}" if unit else base_name
                        result[column_name] = value
            
            # Parse AQI information if present
            if "latest" in data and "aqi" in data["latest"]:
                aqi_data = data["latest"]["aqi"]
                if isinstance(aqi_data, dict):
                    for aqi_key, aqi_info in aqi_data.items():
                        if isinstance(aqi_info, dict) and "value" in aqi_info:
                            result[f"AQI_{aqi_key.upper()}"] = aqi_info["value"]
                            
        except requests.exceptions.HTTPError as e:
            result["Error"] = f"HTTP Error: {e.response.status_code} - {e.response.reason}"
        except requests.exceptions.RequestException as e:
            result["Error"] = f"Request Error: {str(e)}"
        except Exception as e:
            result["Error"] = f"Parsing Error: {str(e)}"
        
        return result
    
    def get_all_devices_data(self, device_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve data for all specified Kaiterra devices.
        
        Args:
            device_ids: List of Kaiterra device identifiers
            
        Returns:
            List of dictionaries containing device data
        """
        all_data = []
        
        for i, device_id in enumerate(device_ids):
            print(f"Fetching Kaiterra device {i+1}/{len(device_ids)}: {device_id}")
            device_data = self.get_device_data(device_id)
            all_data.append(device_data)
        
        return all_data


def consolidate_and_export(awair_data: List[Dict[str, Any]], 
                          kaiterra_data: List[Dict[str, Any]], 
                          output_file: str = "latest_air_quality_data.csv") -> None:
    """
    Consolidate data from both sources and export to CSV.
    
    Args:
        awair_data: List of dictionaries containing Awair device data
        kaiterra_data: List of dictionaries containing Kaiterra device data
        output_file: Name of the output CSV file
    """
    # Combine all data
    all_data = awair_data + kaiterra_data
    
    if not all_data:
        print("Warning: No data to export.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Reorder columns to have common fields first
    priority_columns = ["Source", "Device_ID", "Timestamp_UTC", "Error"]
    other_columns = [col for col in df.columns if col not in priority_columns]
    ordered_columns = priority_columns + sorted(other_columns)
    
    # Reorder DataFrame columns
    df = df[ordered_columns]
    
    # Export to CSV
    df.to_csv(output_file, index=False)
    print(f"\n✓ Data exported successfully to: {output_file}")
    print(f"  Total devices: {len(df)}")
    print(f"  Successful: {len(df[df['Error'].isna()])}")
    print(f"  Failed: {len(df[df['Error'].notna()])}")


def main():
    """Main execution function."""
    
    # Import configuration
    try:
        from config import AWAIR_API_KEY, KAITERRA_API_KEY, AWAIR_DEVICE_IDS, KAITERRA_DEVICE_IDS
    except ImportError:
        print("Error: config.py not found. Please create config.py with your API keys and device IDs.")
        print("See config.example.py for template.")
        return
    
    print("="*60)
    print("Air Quality Data Extractor")
    print("="*60)
    print(f"Start time: {datetime.utcnow().isoformat()}Z\n")
    
    # Extract Awair data
    awair_data = []
    if AWAIR_DEVICE_IDS:
        print(f"Extracting data from {len(AWAIR_DEVICE_IDS)} Awair device(s)...")
        awair_extractor = AwairDataExtractor(AWAIR_API_KEY)
        awair_data = awair_extractor.get_all_devices_data(AWAIR_DEVICE_IDS)
        print(f"✓ Awair extraction complete\n")
    else:
        print("No Awair devices configured.\n")
    
    # Extract Kaiterra data
    kaiterra_data = []
    if KAITERRA_DEVICE_IDS:
        print(f"Extracting data from {len(KAITERRA_DEVICE_IDS)} Kaiterra device(s)...")
        kaiterra_extractor = KaiterraDataExtractor(KAITERRA_API_KEY)
        kaiterra_data = kaiterra_extractor.get_all_devices_data(KAITERRA_DEVICE_IDS)
        print(f"✓ Kaiterra extraction complete\n")
    else:
        print("No Kaiterra devices configured.\n")
    
    # Consolidate and export
    if awair_data or kaiterra_data:
        print("Consolidating data and exporting to CSV...")
        consolidate_and_export(awair_data, kaiterra_data)
    else:
        print("No devices configured. Please add device IDs to config.py")
    
    print(f"\nEnd time: {datetime.utcnow().isoformat()}Z")
    print("="*60)


if __name__ == "__main__":
    main()
