# Islamic Literature Translation Evaluation System (Arabic-to-Target)

An advanced FastAPI-based system using Gemini to evaluate the quality of Arabic-to-Target language translations, focusing on linguistic accuracy, theological precision, and specialized Islamic terminology.

## Key Features

- Precise evaluation based on a custom grading scale (A-J).
- Automated Arabic justification for each assigned grade.
- Support for Back-translation text generation.
- API endpoint for processing Excel files in bulk.

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

## Running the Application

To start the server:

```bash
python -m app.main
```

The application will be available at `http://localhost:8000`.

## Usage

Use the `/evaluate` endpoint to upload an Excel file containing:

- **First Column**: Original Arabic source text.
- **Second Column**: Translated text.

The system will return a new Excel file with the following columns:

- `score_translation`: The numeric/letter grade.
- `justification_translation`: A concise Arabic sentence justifying the score.
- `back_translation`: The generated back-translation text.
