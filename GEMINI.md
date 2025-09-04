# PriceZA Hot Deals Scraper & Dashboard

This project provides a full-stack solution for scraping hot deals from priceza.com, storing the data, and visualizing it through a modern web interface.

## Features

*   **Configurable Scraper Criteria:** Allows dynamic adjustment of scraping parameters (URL, HTML selectors, JSON keys) via a dedicated UI.
*   **Scraper Status Indicator:** The UI now displays a message when the scraper is actively running, providing real-time feedback on data collection.
*   **Automated Web Scraping:** Scrapes hot deals from priceza.com using Selenium to handle dynamic content loading (e.g., "Load More" buttons).
*   **Scheduled Data Collection:** Automatically runs the scraping process every 30 minutes.
*   **RESTful API:** Exposes the scraped data via a FastAPI backend.
*   **Modern User Interface:** A responsive and interactive dashboard built with React and Ant Design.
*   **Structured Data Output:** Scraped data is saved in JSON format.

## Project Structure

The project is organized into two main directories:

*   `backend/`: Contains the Python-based scraping logic and FastAPI server.
*   `frontend/`: Contains the React-based user interface.

## Technologies Used

### Backend
*   **Python:** Core programming language.
*   **FastAPI:** High-performance web framework for building the API, including endpoints for scraper configuration and status.
*   **Pydantic:** Used for data validation and settings management, especially for defining the flexible scraper configuration models.
*   **Selenium:** Web browser automation for dynamic content scraping.
*   **BeautifulSoup4:** HTML parsing library.
*   **APScheduler:** For scheduling the scraping tasks.
*   **WebDriver Manager:** Automatically manages browser drivers for Selenium.

### Frontend
*   **React:** JavaScript library for building user interfaces.
*   **Ant Design:** A comprehensive UI component library for React.
*   **Axios:** Promise-based HTTP client for making API requests.

## Setup and Installation

To get the project up and running, follow these steps:

### 1. Clone the Repository (if applicable)
If this project is in a Git repository, clone it to your local machine:
```bash
# git clone <repository_url>
# cd <project_directory>
```

### 2. Backend Setup

Navigate to the `backend` directory and install the required Python packages:

```bash
cd backend
pip install fastapi uvicorn selenium beautifulsoup4 webdriver-manager python-multipart
```

### 3. Frontend Setup

Navigate to the `frontend` directory and install the Node.js packages:

```bash
cd frontend
npm install
```

## How to Run

You need to run the FastAPI UI server, the scraper, and the frontend development server concurrently.

### 1. Run the FastAPI UI Server

Open your first terminal, navigate to the `backend` directory, and start the FastAPI server:

```bash
cd backend
uvicorn main:app --reload
```
*   The server will start at `http://localhost:8000`.
*   You can view the API documentation at `http://localhost:8000/docs`.

### 2. Run the Scraper

Open your second terminal, navigate to the `backend` directory, and start the scraper:

```bash
cd backend
python scraper_runner.py
```
*   An initial data scrape will run automatically, and subsequent scrapes will occur every 30 minutes.
*   This process will run in the background and continuously update `backend/data/latest_deals.json`.

### 3. Run the Frontend Development Server

Open your third terminal, navigate to the `frontend` directory, and start the React development server:

```bash
cd frontend
npm start
```
*   The React application will open in your browser, usually at `http://localhost:3000`.
*   The UI will automatically refresh when you make changes to the frontend code.

## Running with Docker

This project can be easily run using Docker and Docker Compose. This is the recommended way to get all services (backend API, scraper, and frontend) running together.

### Prerequisites

Make sure you have Docker and Docker Compose installed on your system. You can download them from the official Docker website.

### Build and Run the Application

Navigate to the root directory of the project (where `docker-compose.yml` is located) and run the following command:

```bash
docker-compose up --build
```

This command will:
*   Build the Docker images for the backend and frontend services.
*   Start the `backend_api` (FastAPI server), `scraper_runner` (Python scraper), and `frontend` (React application served by Nginx) services.
*   The `scraper_runner` will automatically start scraping data and update the `backend/data/latest_deals.json` file.

### Accessing the Application

Once all services are up and running:
*   **Backend API:** Access the FastAPI documentation at `http://localhost:8000/docs`.
*   **Frontend Dashboard:** Access the React application at `http://localhost:3000`.

### Stopping the Application

To stop all running Docker containers and remove the networks created by Docker Compose, run the following command from the project root directory:

```bash
docker-compose down
```

### Data Persistence

The `backend/data` directory is mounted as a volume in the `scraper_runner` service. This ensures that the scraped data (`latest_deals.json` and `scraper_status.json`) persists on your host machine even if the Docker containers are removed.

## Usage

Once all three components are running:
*   The React dashboard will display the latest hot deals scraped from PriceZA.
*   The scraper will automatically update the data every 30 minutes in the background, and the frontend will reflect these changes when you refresh the page or click the "Refresh" button.
*   The UI server will remain responsive even when the scraper is actively running.
*   The frontend will display a "Scraping in progress..." message when the scraper is running.