# Islamic Literature Translation Evaluation System (Arabic-to-Target)

An advanced FastAPI-based system using Gemini to evaluate the quality of Arabic-to-Target language translations, focusing on linguistic accuracy, theological precision, and specialized Islamic terminology.

## Key Features

- Precise evaluation based on a custom grading scale (A-J).
- Automated Arabic justification for each assigned grade.
- Support for Back-translation text generation.
- **Interactive Web Dashboard**: A modern, glassmorphism-styled frontend for easy file uploads and downloads.
- **Bulk Processing**: API endpoint and UI support for processing Excel files in bulk.

## Prerequisites

- Python 3.9 or higher.
- Google Gemini API Key.

## Installation

### 1. Set Up Virtual Environment

Open your terminal in the project root directory and run:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables (.env)

Create a `.env` file in the project root and add your API credentials:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-3-flash-preview
```

To start the server:

```bash
python -m app.main
```

The application will be available at `http://localhost:8000`. This will open the **Interactive Dashboard**.

## Usage

### Web Interface (Recommended)

1. Open `http://localhost:8000` in your browser.
2. Drag and drop your Excel file (or click to upload).
3. Click **بدء التقييم** (Start Evaluation).
4. Once processed, the system will automatically trigger a download for your evaluated file.

### API Endpoint

Use the `/evaluate` endpoint directly if you prefer programmatic access.

#### Excel File Requirements

The uploaded file must contain:

- **First Column**: Original Arabic source text.
- **Second Column**: Translated text.

#### Output

The system returns an Excel file with the following columns:

- `score_translation`: The numeric/letter grade.
- `justification_translation`: A concise Arabic sentence justifying the score.
- `back_translation`: The generated back-translation text.
