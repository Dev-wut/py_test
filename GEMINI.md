# PriceZA Hot Deals Scraper & Dashboard

This project is a full-stack solution for scraping Hot Deals from priceza.com, storing the data, and visualizing it through a modern web interface.

## Features

*   **Configurable Scraper Criteria:** Allows dynamic adjustment of scraping parameters (URL, HTML selectors, JSON keys) via a dedicated UI.
*   **Automated Web Scraping:** Scrapes hot deals from priceza.com using Selenium to handle dynamic content loading (e.g., "Load More" buttons).
*   **Scheduled Data Collection:** The scraper runs automatically every 30 minutes.
*   **RESTful API:** Exposes the scraped data via a backend built with FastAPI.
*   **Modern User Interface:** A responsive and interactive dashboard built with React and Ant Design.
*   **Scraper Status Indicator:** The UI displays a message when the scraper is actively running, providing real-time feedback on data collection.
*   **Structured Data Output:** Scraped data is saved in JSON format.

## Installation

To get this project running, follow these steps:

1.  **Backend Setup:**
    Navigate to the `backend` directory and install the required Python packages:
    ```bash
    cd backend
    pip install fastapi uvicorn selenium beautifulsoup4 webdriver-manager python-multipart apscheduler
    ```

2.  **Frontend Setup:**
    Navigate to the `frontend` directory and install the required Node.js packages:
    ```bash
    cd frontend
    npm install
    ```

## How to Run

You need to run the FastAPI UI Server, the Scraper, and the Frontend Development Server concurrently in separate terminals:

### 1. Run the FastAPI UI Server

Open your first terminal, navigate to the `backend` directory, and start the FastAPI Server:

```bash
cd backend
uvicorn main:app --reload
```
*   The server will start at `http://localhost:8000`
*   You can view the API documentation at `http://localhost:8000/docs`

### 2. Run the Scraper

Open your second terminal, navigate to the `backend` directory, and start the Scraper:

```bash
cd backend
python scraper_runner.py
```
*   An initial data scrape will run immediately, and subsequent scrapes will occur every 30 minutes.
*   This process will run in the background and continuously update the `backend/data/latest_deals.json` file.

### 3. Run the Frontend Development Server

Open your third terminal, navigate to the `frontend` directory, and start the React Development Server:

```bash
cd frontend
npm start
```
*   The UI will automatically refresh when you make changes to the frontend code.

## Running with Docker

This project can be easily run using Docker and Docker Compose. This is the recommended way to get all services (Backend API, Scraper, and Frontend) running together.

### Prerequisites

Make sure you have Docker and Docker Compose installed on your system. You can download them from the official Docker website.

### Build and Run the Application

Navigate to the root directory of the project (where `docker-compose.yml` is located) and run the following command:

```bash
docker-compose up --build
```

This command will:
*   Build the Docker images for the Backend and Frontend services.
*   Start the `backend_api` (FastAPI server), `scraper_runner` (Python scraper), and `frontend` (React application served by Nginx) services.
*   The `scraper_runner` will automatically start scraping data and update the `backend/data/latest_deals.json` file.

### Accessing the Application

Once all services are running:
*   **Backend API:** Access the FastAPI documentation at `http://localhost:8000/docs`
*   **Frontend Dashboard:** Access the React application at `http://localhost:3000`

### Stopping the Application

To stop all running Docker containers and remove the networks created by Docker Compose, run the following command from the project's root directory:

```bash
docker-compose down
```

### Data Persistence

The `backend/data` directory is mounted as a Volume in the `scraper_runner` service. This ensures that the scraped data (`latest_deals.json` and `scraper_status.json`) persists on your host machine even if the Docker containers are removed.

## Things to know

*   **Separation of Concerns:** The backend is divided into two main parts: the FastAPI UI Server and the Scraper Server, which run separately. This ensures that the UI Server remains responsive even while the Scraper is running.
*   **Scraper Status:** The scraper creates and updates the `backend/data/scraper_status.json` file to indicate whether it is currently running. The UI Server reads this file via the `/api/scraper_status` API endpoint, and the Frontend uses this information to display a "Scraping in progress..." message to the user.
*   **Scraper Configuration:** The scraper uses the `backend/data/scraper_config.json` file to configure the URL, HTML selectors (e.g., `tag`, `class`, `id`, `attrs`), and JSON keys for the scraped data. You can edit this configuration through the `/scraper-criteria` UI page. `attrs` is a dictionary of additional HTML attributes used to precisely identify elements (e.g., `{"href": true, "onmousedown": true}` for a link).

## Contributing

Please avoid committing generated files such as backups, __pycache__ directories, log files, and scraped datasets. These are ignored via `.gitignore` and should be regenerated locally.
