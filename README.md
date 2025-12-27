# StoreFromNET - Video Downloader

A Flask-based web application that allows users to download videos from various platforms (like YouTube) using `yt-dlp`.

**Status: Working prototype (Not fully completed)**

## Features

- **Video Information Fetching**: Extracts video title, thumbnail, and available resolutions without downloading.
- **Quality Selection**: Choose from available resolutions (e.g., 1080p, 720p) or "Best Quality".
- **Automatic Merging**: Uses `yt-dlp` to download the best video and audio streams and merges them into an MP4 container.
- **Auto-Cleanup**: Automatically deletes downloaded files from the server after they are sent to the user to save space.
- **Modern UI**: Dark-themed tailored interface built with Tailwind CSS.

## Prerequisites

- Python 3.7+
- [FFmpeg](https://ffmpeg.org/download.html) (Required for merging video and audio streams)

## Installation

1.  **Clone the repository** (or download source):
    ```bash
    git clone <your-repo-url>
    cd StoreFromNET
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Start the application**:
    ```bash
    python app.py
    ```

2.  **Open in Browser**:
    Navigate to [http://localhost:5000](http://localhost:5000).

3.  **Download a Video**:
    - Paste a video URL (e.g., from YouTube).
    - Click "Fetch Info".
    - Select your desired quality.
    - Click "Download Video".

## Project Structure

- `app.py`: Main Flask application handling routes and logic.
- `templates/index.html`: Frontend user interface.
- `downloads/`: Temporary storage for downloaded files (auto-cleared).
- `requirements.txt`: Python dependencies.
- `test_api.py`: Script to test the backend API endpoints.

## Known Issues / To-Do

- This is a work in progress.
- Error handling can be improved for edge cases.
- UI is currently a single page.

## License

[MIT](https://choosealicense.com/licenses/mit/)
