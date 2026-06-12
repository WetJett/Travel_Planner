# Travel Planner API
This project is a backend service for a travel planning application, built with FastAPI and SQLAlchemy. It enables users to create travel projects, manage destinations (places), and track travel progress.

Note: This implementation is a Minimum Viable Product (MVP), developed within a restricted timeframe. While it covers the requested core functionality and database integrity, it is currently in a "raw" state. Further improvements regarding error handling, exhaustive input validation, and unit testing are planned for future iterations.

## Getting Started

Prerequisites

  - Python 3.10+
  - pip

### Local Setup

1. Clone the repository and navigate to the project folder.
2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Start the development server:

   ```sh
   uvicorn main:app --reload
   ```
Access the API documentation at http://127.0.0.1:8000/docs

### Running with Docker

   ```sh
   docker build -t travel-planner .
   docker run -p 8000:8000 travel-planner
   ```
