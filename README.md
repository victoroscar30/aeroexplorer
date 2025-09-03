### Exploratory Data Analysis (EDA) - `01_exploration.ipynb`

Before designing the pipeline and database, a thorough understanding of the flight data is crucial. **The EDA phase aimed to uncover trends, distributions, and potential anomalies** within the data retrieved from the OpenSky API. Rather than focusing on raw numbers, the analysis emphasizes insights, motivations, and implications for the subsequent pipeline and database design.

#### Objectives

* **Acquire and Structure Data:** Get the raw flight data from the OpenSky Network API and transform it into a clean, structured pandas DataFrame for easy manipulation and analysis.

* **Assess Data Quality:** Identify and document key data quality issues, such as missing values, physically impossible data points (e.g., negative altitudes), and measurement errors (e.g., unrealistic speeds or vertical rates).

* **Handle Outliers:** Develop a strategy to address and either correct, flag, or remove anomalous data points that fall outside of realistic physical bounds.

* **Visualize Key Distributions:** Create initial visualizations, such as the bar chart of flight origins, to gain a preliminary understanding of the data's characteristics and geographical distribution.

* **Prepare Data for Further Analysis:** Ultimately, the objective is to clean and prepare the dataset so that it can be reliably used for more advanced analysis, such as building predictive models or deriving deeper insights.

#### Key Analytical Steps
1. **Data Ingestion and Transformation**
The analysis begins by fetching raw data from the OpenSky Network API in a nested JSON format. This raw data is then processed and converted into a structured pandas DataFrame. This transformation is crucial as it organizes the data into a tabular format, which is essential for efficient data manipulation, filtering, and statistical analysis. This is accomplished by creating a pandas DataFrame named `df_final`.

2. **Data Cleaning and Quality Assessment**
The core of this initial analysis is to understand the quality of the data and identify any issues that could skew future results. Several key observations and actions were made:

    * **Considering Missing Data:** Columns like `category` and `sensors` are noted for potential removal in a later data pipeline step due to a complete lack of usable data.This is a form of feature reduction, which simplifies the dataset and removes irrelevant noise. It's a standard practice to drop features with no variance or missing values.
    * **Timestamp Conversion:** Raw Unix timestamps are converted into a human-readable datetime format, which is vital for any time-series analysis or for calculating time-based metrics like flight duration.
    Outlier and Anomaly Detection: The analysis makes specific notes about identifying values that fall outside of a realistic physical range.

    * **Altitude:** It notes that `baro_altitude` and `geo_altitude` can have small negative values. The correct approach is to **either set these to zero or filter them out, as negative altitude is physically impossible in this context.**

    * **Vertical Rate:** The notebook points out extremely high or low values for `vertical_rate` (e.g., -165 m/s), indicating sensor error or data corruption. The proposed solution of **either capping the values within a realistic range (-30 to +30 m/s) or discarding them is a robust way to handle such outliers.**

    * **Velocity:** The analysis flags velocities above ~320 m/s as potentially anomalous. This suggests a need for a deeper look into these specific data points to understand if they represent a valid, albeit rare, event (like a military jet) or are simply measurement errors.
3. **Flight Behavior and Characteristics**

    **Spatial Distribution:**
The analysis examines the geographical spread of flight data. A bar chart of `origin_country` highlights where most active flights originate.

    * **Objective:** Understand the global or regional concentration of flights.

    * **Method:** Counting occurrences of each country in `origin_country` using `value_counts()`, then visualizing with a bar chart.

    * **Takeaway:** Provides insight into dataset biases, indicating if certain regions dominate the data, which informs decisions for subsequent analyses or data supplementation.

    **Temporal Distribution:**
    Although not explicitly visualized, temporal analysis is prepared through timestamp conversion.

    * **Objective:** Enable analysis of flight patterns over time, including peak activity periods.
    * **Method:** Unix timestamps (`time_position`, `last_contact`) are converted to datetime format, allowing time-based calculations.
    * **Takeaway:** Prepares the dataset for analyses like flight volume over time, flight duration, and lag between recorded events.

    **Altitude, Velocity, and Vertical Rate:**
    Key flight characteristics are explored to identify patterns and anomalies.

    * **Objective:** Understand flight dynamics and detect unusual behaviors.
    * **Method:** Scatter plots of `baro_altitude` vs `velocity` and `vertical_rate` vs `baro_altitude`; histograms of `vertical_rate`.
    * **Takeaway**: Visualizations reveal normal flight profiles, highlight outliers, and provide context for further analysis or model validation.

#### Key Takeouts and Insights

* **Altitude:** Small negative values in baro_altitude and geo_altitude are physically impossible and should be rounded to 0.

* **Vertical Rate:** Extreme values (e.g., -165 m/s) indicate sensor errors and should be discarded or capped to a realistic range (-30 to +30 m/s).

* **Velocity:** Speeds above ~320 m/s are rare and should be reviewed as anomalies.

* **Feature Reduction:** Columns with missing or irrelevant data (category, sensors, possibly squawk) can be removed to simplify the dataset.

This data cleaning and quality assessment ensures the dataset is reliable and consistent. Handling missing values, converting timestamps, and addressing outliers in altitude, vertical rate, and velocity provide a strong foundation for accurate analysis and future pipeline automation. These steps not only improve the accuracy of subsequent analyses but also guide the design of the **data pipeline**, enabling more efficient, automated handling of incoming flight data.

___
### Pipeline - `pipeline.py`
This data engineering pipeline is designed to extract, transform, and load flight data from the OpenSky Network API. It automates the process of collecting raw data, applying cleaning and transformation rules, and then storing the processed data in a MongoDB collection. The pipeline's modular structure makes it easy to maintain and extend for future stages.

#### Pipeline Flow
The pipeline follows a simple **Extract-Transform-Load (ETL)** approach, where each stage is encapsulated in a separate Python module to ensure a separation of responsibilities.

##### Pipeline Diagram
The data flow follows a clear sequence, orchestrated by the main script `pipeline.py`.

```mermaid
graph TD
    subgraph Orchestration
        A[pipeline.py] --> B(Orchestration & Scheduling);
    end

    subgraph Pipeline
        B --> C[fetch_data.py];
        C --> D[transform.py];
        D --> E[load.py];
    end

    subgraph Dependencies
        G[auth_opensky.py] --> C;
    end
    
    E --> F{Database or File};
    F --> I(MongoDB);
    F --> H(CSV);
```
#### Execution Map
1. **Orchestration:** The `pipeline.py` script is the entry point, scheduling a complete job to run every 30 seconds.

2. **Extraction:** The job starts by collecting raw data (`fetch_data.py`) from the OpenSky API.

3. **Transformation:** Next, the raw DataFrame is standardized, cleaned, and validated (`transform.py`).

4. **Loading:** The processed data is then loaded into its final destination (`load.py`).

##### Component Catalog

| File/Module        | Functions/Entrypoints                           | Inputs                           | Outputs/Artifacts                       | Dependencies (int/ext)                       | How to run                   | Notes                                                                 |
|-------------------|-----------------------------------------------|---------------------------------|---------------------------------------|---------------------------------------------|-------------------------------|----------------------------------------------------------------------|
| `pipeline.py`      | `job()`, `if __name__ == "__main__"`          | N/A                             | Console logs                           | schedule, time, fetch_data, transform, load | `python pipeline.py`          | Main orchestrator. Scheduled to run the full pipeline every 30s. Can be stopped with Ctrl+C. |
| `auth_opensky.py`  | `OpenSkyAuth` class, `obter_novo_token()`, `get_token()` | Credentials via environment variables (.env) | API `access_token` and `expires_in` | os, requests, time, dotenv                  | N/A (invoked internally)      | Handles authentication and token renewal for the OpenSky API.       |
| `fetch_data.py`    | `fetch_opensky()`, `if __name__ == "__main__"` | `access_token` from API         | Pandas DataFrame (`df`) with raw flight data | requests, json, datetime, pathlib, pandas, auth_opensky | `python fetch_data.py`        | Extracts and normalizes flight data from OpenSky API. Creates initial DataFrame. |
| `transform.py`     | `transform_flights()`                         | DataFrame from `fetch_data.py`  | Clean and formatted Pandas DataFrame  | pandas                                      | N/A (invoked internally)      | Cleans, validates, and enriches data. Handles nulls, removes unused columns, converts types. |
| `load.py`          | `load_to_csv()`, `load_to_mongo()`           | DataFrame from `transform.py`   | CSV file (`data/processed/*.csv`) or MongoDB documents | pandas, pymongo                             | N/A (invoked internally)      | Saves processed data to CSV or MongoDB depending on the chosen method. |

#### Configuration and Credentials
Credentials for OpenSky Network API access are stored in a `.env` file at the project root. The `auth_opensky.py` module uses the `dotenv` library to load these environment variables.

**Required variables in `.env:`**

* `OPENSKY_USERNAME`: Username for your OpenSky account.

* `OPENSKY_PASSWORD`: Password for your OpenSky account.

* `TOKEN_URL`: URL of the token endpoint for authentication. 

>[!IMPORTANT]
>The token URL is provided by OpenSky and must be configured in this variable.

MongoDB credentials, such as `mongo_uri`, `db_name`, and `collection_name`, are configured with default values directly in the `load_to_mongo()` function.

#### Data and Schemas

**Data Source:** OpenSky Network flight states API `/api/states/all`

**Input Format:** JSON with a nested list of flight states.  

**Output Format:**
- **CSV:** Files with the `opensky_data_` prefix and a timestamp suffix (`YYYYMMDD_HHMMSS`) saved in `data/processed/`.
- **MongoDB:** Documents inserted into the `air_traffic` collection of the `flightdeck` database.

##### Data Schema (after transformation)

| Field            | Data Type | Notes                                                       |
|------------------|-----------|-------------------------------------------------------------|
| time             | datetime  | Timestamp of the API response.                              |
| icao24           | str       | Unique aircraft identifier.                                 |
| callsign         | str       | Call sign (stripped of whitespace).                         |
| origin_country   | str       | Country of origin.                                          |
| time_position    | datetime  | Last position timestamp.                                    |
| last_contact     | datetime  | Last known contact.                                         |
| longitude        | float     | Geographical position.                                      |
| latitude         | float     | Geographical position.                                      |
| baro_altitude    | float     | Barometric altitude (no negative values).                   |
| on_ground        | bool      | True if the aircraft is on the ground.                      |
| velocity         | float     | Velocity.                                                   |
| true_track       | float     | True flight direction.                                      |
| vertical_rate    | float     | Rate of ascent/descent (capped between -30 and +30).        |
| geo_altitude     | float     | Geometric altitude (no negative values).                    |
| spi              | bool      | Whether flight status indicates special purpose indicator.  |
| position_source  | int       | Position source.                                            |
| velocity_anomaly | bool      | True if the velocity is greater than 320 m/s.               |

**Removed Columns:** `category`, `sensors`, and `squawk` are dropped in the transformation step due to a lack of usable data.

#### Quality, Validation, and Logs

- **Validation Rules:**
  - Negative altitudes (`baro_altitude`, `geo_altitude`) are adjusted to `0`.
  - `vertical_rate` is capped between **-30** and **+30 m/s**.
  - Velocities above **320 m/s** are flagged as anomalies.

- **Logs:** Console messages track progress, including:
  - Token generation (`auth_opensky.py`).
  - Number of saved records (`pipeline.py`).
  - Load errors (`load.py`).

- **Error Handling:**
  - **Extraction:** `fetch_data.py` uses `resp.raise_for_status()` for HTTP errors (401, 404, etc.).
  - **Loading:** `load_to_mongo()` uses `try...except BulkWriteError` with `ordered=False` to continue inserting even if some documents fail.

#### Performance and Scalability

- **Batch Processing:** Processes data in DataFrames, inserting multiple docs into MongoDB via `insert_many()`.  
- **Token Management:** Cached and proactively renewed 60s before expiration.  
- **Limitations:** Current scheduling (`schedule`) is lightweight and lacks retries, fault tolerance, or DAG visualization (better suited for Airflow, Prefect, or Dagster).

#### Testing and Reproducibility

- **Tests:** Basic via `if __name__ == "__main__"` in `fetch_data.py` and `pipeline.py`.  
- **Dependencies:**
  - `python-dotenv`
  - `requests`
  - `schedule`
  - `pandas`
  - `pymongo`
- **Reproducibility:** Requires only the dependencies above and a properly configured `.env` file.

#### End-to-End Execution

1. Create a `.env` file at the project root and configure variables:

   ```ini
   OPENSKY_USERNAME="your_username"
   OPENSKY_PASSWORD="your_password"
   TOKEN_URL="https://opensky-network.org/api/token"
   ```
2. Run the pipeline from the terminal:

    ```python
    python pipeline.py
    ```

3. To stop execution, use Ctrl+C.

#### Monitoring and Metrics

- **Current:** Monitoring is limited to console messages showing execution status, number of saved records, and token renewal.  
- **Future Improvements:** Integration with robust logging (e.g., Loguru) or metrics platforms (e.g., Prometheus) could provide better observability.

#### Limitations and Future Improvements

- **Orchestration:** Replace `schedule` with a production-grade tool (e.g., Airflow, Prefect, Dagster).  
- **Configuration:** Centralize settings (`mongo_uri`, `db_name`, etc.) in a dedicated file (`config.py` or `config.yaml`).  
- **Data Ingestion:** Add schema validation (e.g., Pydantic) to ensure input data consistency.  
- **Persistence:** Make the choice between `CSV` and `MongoDB` output configurable instead of hardcoded.  
- **Testing:** Expand test coverage with unit tests (pytest) and integration tests for the full pipeline flow.

>[!NOTE]
> Advanced monitoring, observability, and orchestration tools (e.g., Airflow, Prefect, Dagster, Prometheus) were considered during the design phase.  
> However, since this project is intended as a **demonstration**, these technologies were **intentionally not implemented** to keep the pipeline simple and focused on core ETL concepts.  
> They represent **natural next steps** for scaling this pipeline into a **production-ready system**.
---
### Design Decisions

- **Single collection:**  
  All records are stored in a single MongoDB collection. This decision is based on MongoDB's efficiency in handling large volumes of data without needing multiple collections, unlike SQL databases. This approach keeps the architecture simple and facilitates aggregate queries across the entire dataset.

- **Primary key (`_id` default):**  
  Each document uses MongoDB's default `_id` as the primary key, ensuring uniqueness and simplifying insertion and update logic. There was no need for composite or artificial keys at this demonstration stage.

- **Data retention / temporal window:**  
  Data is kept within a fixed temporal window, suggested at 24 hours. This strategy prevents indefinite collection growth and ensures the demonstration remains lightweight and fast. More advanced retention or archival policies can be added in a future version.

- **Indexes (future considerations):**  
  Although not implemented at this stage, indexes on critical fields such as `icao24` and `origin_country` could be added to accelerate frequent queries and filters. The decision to skip indexes for now keeps the pipeline simple and suitable for test volumes.

- **Scalability strategies (future considerations):**  
  Strategies like sharding, temporal partitioning, or replication were not considered at this initial phase. They remain potential evolutions if the project scales to production, allowing higher database scalability and availability.

- **Trade-offs:**  
  Some decisions were made prioritizing **simplicity, learning, and demonstration of concept** over complex optimizations or advanced production practices. Each point above was carefully evaluated to balance **ease of use**, **clarity for the reader**, and **possible future evolutions**.
---

## Acknowledgements
This project uses data from the OpenSky Network. We thank the OpenSky team for providing access to their ADS-B sensor network.

Reference:
Matthias Schäfer, Martin Strohmeier, Vincent Lenders, Ivan Martinovic and Matthias Wilhelm.
"Bringing Up OpenSky: A Large-scale ADS-B Sensor Network for Research".
In Proceedings of the 13th IEEE/ACM International Symposium on Information Processing in Sensor Networks (IPSN), pages 83-94, April 2014.

Website: [https://opensky-network.org](https://opensky-network.org)

_This project is not affiliated with OpenSky; it is for educational purposes only_
