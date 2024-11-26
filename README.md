# MVG Display

A simple web app to show real-time tram and bus schedules, designed to integrate with Flask (backend) and React (frontend).

## Features

- Real-time schedule updates for trams and buses.
- Color-coded schedules for easy decision-making.
- Integration for multi-leg journeys.

## Directory Structure

```plaintext
mvg/
├── backend/
│   ├── tram_times.py       # Flask backend logic
│   ├── requirements.txt    # Python dependencies
│   ├── templates/          # HTML templates for Flask
│   ├── static/             # Static assets (CSS, JS)
├── frontend/
│   ├── public/             # Public assets for React
│   ├── src/                # React source code
├── Dockerfile              # Docker setup
├── docker-compose.yml      # Multi-service setup
└── README.md               # Documentation
