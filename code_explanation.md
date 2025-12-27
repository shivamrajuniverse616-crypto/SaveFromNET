# Code Explanation
This application is a **Flask-based video downloader** that utilizes `yt-dlp` to fetch video information and download videos from various platforms (like YouTube).

## System Architecture

The system consists of three main components:
1.  **Backend (`app.py`)**: A Flask web server that provides API endpoints.
2.  **Frontend (`templates/index.html`)**: A user interface built with HTML, Tailwind CSS, and JavaScript.
3.  **Test Script (`test_api.py`)**: A standalone Python script to test the backend API.

## File Breakdown and Logic

### 1. `app.py` (The Backend)
This is the core of the application. It runs a web server on port 5000.

*   **Libraries**:
    *   `flask`: Handles web routes and HTTP requests.
    *   `yt-dlp`: A powerful library to download videos from thousands of websites.
    *   `flask_cors`: Allows the frontend to communicate with the backend even if hosted on different ports (though here they are on the same origin).

*   **Routes**:
    *   `/` (GET): Serves the `index.html` page to the user.
    *   `/get_info` (POST):
        *   Receives a JSON object with a `url`.
        *   Uses `yt-dlp` to extract metadata (title, thumbnail, available formats) **without** downloading the video.
        *   Filters and sorts available video resolutions (e.g., 1080p, 720p).
        *   Returns this data to the frontend so the user can choose a quality.
    *   `/download` (POST):
        *   Receives a `url` and a chosen `quality`.
        *   Configures `yt-dlp` to download the specific format.
        *   If "Best Quality" is chosen, it merges the best video and best audio streams into an MP4 file.
        *   Saves the file to a `downloads` folder.
        *   Returns a URL path to the downloaded file.
    *   `/downloads/<filename>` (GET):
        *   Serves the actual file to the user's browser.
        *   **Cleanup**: Automatically deletes the file from the server after the request completes to save space (`@after_this_request`).

### 2. `test_api.py` (The Tester)
A simple utility to verify the backend without using the browser.

*   It constructs a JSON payload with a sample YouTube URL.
*   Sends a POST request to `http://127.0.0.1:5000/get_info`.
*   Prints the server's response code and the JSON data (video details).
*   **Usage**: Run `python test_api.py` while `app.py` is running to verify the API returns 200 OK and correct video data.

### 3. `templates/index.html` (The Frontend)
A single-page interface.

*   **Design**: Uses Tailwind CSS for a modern, dark-themed look with animations.
*   **Logic**:
    *   `Fetch` button sends the URL to `/get_info`.
    *   Populates a dropdown with available resolutions.
    *   `Download` button sends the selection to `/download`.
    *   Redirects the browser to the file URL to trigger the actual download.

## How it Works Together
1.  **User** opens the app in a browser.
2.  **User** pastes a link and clicks "Fetch".
3.  **Frontend** calls `/get_info`.
4.  **Backend** asks `yt-dlp` for details and returns them.
5.  **User** selects "1080p" and clicks "Download".
6.  **Frontend** calls `/download`.
7.  **Backend** downloads the video, saves it, and gives the frontend a link.
8.  **Frontend** navigates to that link.
9.  **Backend** serves the file and then **deletes** it from the server.
