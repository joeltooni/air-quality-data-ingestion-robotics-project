# Air Quality Data Ingestion Service

**Awair Omni & Kaiterra Sensedge Mini**

A production-ready Python service that implements a consolidated data ingestion pipeline for retrieving and standardizing real-time air quality sensor readings from two vendor platforms: Awair Omni and Kaiterra Sensedge Mini. This solution overcomes challenges posed by outdated or complex vendor APIs by providing a reliable, authenticated script capable of fetching the latest sensor data from multiple devices across both platforms and compiling results into a single, standardized CSV file.

---

## 1. Project Overview

This project delivers a single, consolidated data ingestion service built to retrieve and standardize real-time air quality sensor readings from:

- **Awair Omni** devices via the Enterprise Dashboard API
- **Kaiterra Sensedge Mini** devices via the Public API

### Core Objectives

The solution addresses key challenges in multi-vendor air quality monitoring:

- **API Complexity**: Simplifies interaction with two distinct vendor APIs with different authentication mechanisms and data structures
- **Data Standardization**: Normalizes nested and disparate JSON responses into a unified, flat CSV format
- **Reliability**: Implements comprehensive error handling to ensure graceful degradation when individual devices fail
- **Rate Limit Compliance**: Manages API request throttling to maintain compliance with vendor limitations

---

## 2. Technical Architecture and Features

The solution is architected around two primary API integration modules, managed by a central execution flow using the `requests` and `pandas` libraries.

### 2.1 Initialization and Credential Management

**Action**: Initialized Project Environment and Secured API Credentials

- **Setup**: The environment requires only standard Python 3.7+ with the `requests` library (for HTTP communication) and the `pandas` library (for data structuring and CSV generation)
- **Secure Configuration**: Dedicated configuration sections (`config.py`) manage all necessary credentials (API Keys and Unique Device Identifiers) in one place, ensuring clean separation between configuration and logic
- **Modularity**: Configuration template (`config.example.py`) provided for easy deployment across different environments

### 2.2 Awair Omni Data Extraction Module

**Action**: Developed and Tested Awair Omni Latest Data Extraction Module

- **API Target**: Awair Enterprise Dashboard API (`/v1/users/self/devices/omni/{device_id}/air-data/latest`)
- **Authentication**: Utilizes the custom `x-api-key` header for authorization, reflecting the current Enterprise API standard
- **Data Processing**: The module is specifically engineered to:
  - Handle the nested JSON response from the `/air-data/latest` endpoint
  - Flatten the internal `sensors` array structure
  - Map technical keys (`co2`, `voc`, `pm25`) to human-readable column headers (`CO2_ppm`, `VOC_ppb`, `PM2.5_µg/m³`)
  - Extract timestamp and proprietary Awair Score metrics
- **Rate Limiting**: Implements 6-second delays between requests to comply with the 10 requests/minute API limit

### 2.3 Kaiterra Sensedge Mini Data Extraction Module

**Action**: Developed and Tested Kaiterra Sensedge Mini Latest Data Extraction Module

- **API Target**: Kaiterra Public API (`/v1/lasereggs/{device_id}`)
- **Authentication**: Utilizes the standard `X-API-Key` header for authorization alongside the device's Unique Device ID (UDID)
- **Data Processing**: The function employs specialized logic to:
  - Parse the highly nested Kaiterra response structure (`latest.data` and `latest.aqi`)
  - Accurately extract the latest value and retain the corresponding unit for each air quality parameter
  - Generate consistent column names with embedded units (e.g., `PM2.5_µg/m³`, `Temperature_°C`)
  - Extract AQI (Air Quality Index) values when available

### 2.4 Data Consolidation and CSV Output

**Action**: Consolidated Extracted Data and Generated CSV Output

- **Consolidation**: The central `main()` function manages:
  - Sequential execution of all device calls from both platforms
  - Aggregation of all successful and failed records into a single list
  - Preservation of error messages for failed requests
- **Output Generation**: The combined data is processed by pandas to:
  - Create a unified DataFrame handling disparate data fields from both APIs
  - Automatically align columns across different device types
  - Prioritize common fields (`Source`, `Device_ID`, `Timestamp_UTC`, `Error`) in the output
  - Generate a harmonized, column-aligned output file: `latest_air_quality_data.csv`

### 2.5 Error Handling and Stability

**Action**: Implemented Robust Error Handling and Rate Limit Management

- **Error Management**: Comprehensive `try/except` logic using `response.raise_for_status()` detects and handles:
  - HTTP errors (401/403 authentication failures, 404 not found, 5xx server errors)
  - Network connectivity issues and timeouts
  - JSON parsing errors and unexpected data structures
  - Failure records are explicitly tagged with descriptive error messages in the final CSV
- **Rate Limiting**: Deliberate `time.sleep(6)` intervals introduced between Awair device API calls to:
  - Prevent API throttling
  - Maintain compliance with vendor's documented request rate limitations
  - Ensure reliable, uninterrupted data collection

### 2.6 Validation and Documentation

**Action**: Final Testing, Validation, and Code Documentation

- **Code Quality**: The final script includes:
  - Detailed docstrings for all classes and methods
  - Type hints for function parameters and return values
  - Inline comments defining variable purposes, data structures, and logic flow
  - High maintainability through object-oriented design patterns
- **Readiness**: The solution is validated to consistently deliver a standardized output schema, ready for:
  - Immediate use in reporting dashboards
  - Integration into downstream data pipeline steps
  - Historical data aggregation and trend analysis

---

## 3. Features

- ✅ **Dual API Integration**: Supports both Awair Enterprise Dashboard API and Kaiterra Public API
- ✅ **Real-time Data**: Fetches only the latest sensor readings (no historical data)
- ✅ **Robust Error Handling**: Gracefully handles API failures and logs errors in the output CSV
- ✅ **Rate Limiting**: Implements 6-second delays for Awair API calls (10 requests/minute limit)
- ✅ **Smart Data Parsing**: Automatically maps nested JSON structures to flat, readable CSV columns
- ✅ **Unit Preservation**: Maintains sensor units in column names (e.g., `PM2.5_µg/m³`, `Temperature_°C`)
- ✅ **Single CSV Output**: Consolidates all device data into one clean file
- ✅ **Production-Ready**: Comprehensive error handling, logging, and validation

---

## 4. Usage Instructions

### Requirements

- Python 3.7+
- `requests` library
- `pandas` library

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API credentials**:

   ```bash
   cp config.example.py config.py
   ```

   Then edit `config.py` and add your:
   - Awair API key (obtain from [Awair Developer Portal](https://developer.getawair.com/))
   - Kaiterra API key (obtain from [Kaiterra Developer Portal](https://www.kaiterra.com/dev/))
   - Device IDs for each platform

### Configuration

Edit `config.py` with your specific details:

```python
# Awair Configuration
AWAIR_API_KEY = "your_actual_api_key"
AWAIR_DEVICE_IDS = ["12345", "67890"]  # Your Awair device IDs

# Kaiterra Configuration
KAITERRA_API_KEY = "your_actual_api_key"
KAITERRA_DEVICE_IDS = ["00000000-0001-0001-0000-00007e57c0de"]  # Your Kaiterra device IDs
```

### Execution

Run the script:

```bash
python air_quality_extractor.py
```

The script will:

1. Connect to each configured Awair device (with rate limiting)
2. Connect to each configured Kaiterra device
3. Extract the latest sensor readings
4. Consolidate all data into a single DataFrame
5. Export to `latest_air_quality_data.csv`

---

## 5. Output Format

The CSV file includes:

### Common Columns (All Devices)

- `Source`: Device manufacturer (Awair or Kaiterra)
- `Device_ID`: Unique device identifier
- `Timestamp_UTC`: UTC timestamp of the reading
- `Error`: Error message (if request failed)

### Awair Columns

- `Temperature_°C`: Temperature in Celsius
- `Humidity_%`: Relative humidity percentage
- `CO2_ppm`: Carbon dioxide in parts per million
- `VOC_ppb`: Volatile organic compounds in parts per billion
- `PM2.5_µg/m³`: Fine particulate matter
- `PM10_µg/m³`: Coarse particulate matter
- `Awair_Score`: Proprietary air quality score

### Kaiterra Columns

- `PM2.5_µg/m³`: Fine particulate matter
- `PM10_µg/m³`: Coarse particulate matter
- `TVOC_ppb`: Total volatile organic compounds
- `Temperature_°C`: Temperature in Celsius
- `Humidity_%RH`: Relative humidity
- `CO2_ppm`: Carbon dioxide
- `AQI_*`: Air Quality Index values (if available)

---

## 6. Error Handling and Rate Limiting

### Error Handling

The script includes comprehensive error handling:

- **HTTP Errors** (401, 403, 404, etc.): Logged with status code and reason
- **Network Errors**: Connection timeouts, DNS failures, etc.
- **Parsing Errors**: Unexpected JSON structure or missing fields

Failed requests are recorded in the CSV with error details in the `Error` column, while successful requests continue processing.

### Rate Limiting

**Awair API**: 10 requests per minute limit

- The script automatically waits 6 seconds between each Awair device request
- This ensures compliance with API rate limits

**Kaiterra API**: No rate limiting implemented (check API documentation for current limits)

---

## 7. Example Output

```text
Fetching Awair device 1/2: 12345
Fetching Awair device 2/2: 67890
✓ Awair extraction complete

Fetching Kaiterra device 1/1: 00000000-0001-0001-0000-00007e57c0de
✓ Kaiterra extraction complete

Consolidating data and exporting to CSV...

✓ Data exported successfully to: latest_air_quality_data.csv
  Total devices: 3
  Successful: 3
  Failed: 0
```

---

## 8. API Documentation

- **Awair Enterprise Dashboard API**: <https://docs.developer.getawair.com/>
- **Kaiterra Public API**: <https://www.kaiterra.com/dev/docs/api/>

---

## 9. Troubleshooting

### ImportError: No module named 'config'

- Make sure you've copied `config.example.py` to `config.py`

### HTTP 401 Unauthorized

- Verify your API keys are correct in `config.py`
- Check that your API keys are active and haven't expired

### HTTP 404 Not Found

- Verify your device IDs are correct
- Ensure devices are registered to your account

### No data in CSV

- Check that you've added device IDs to the configuration lists
- Verify both API keys and device IDs are configured
