import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.model.gemini_3_flash import Gemini3Flash
from app.service.evaluation_service import EvaluationService

app = FastAPI()

# Mount frontend directory for static assets (CSS, JS)
frontend_dir = os.path.join(os.getcwd(), "frontend")
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

llm_model = Gemini3Flash(settings.GEMINI_API_KEY, settings.GEMINI_MODEL_NAME)
evaluation_service = EvaluationService(llm_model)

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.post("/evaluate")
def evaluate_excel(get_justification: str = Form("true"), file: UploadFile = File(...)):
    # Robustly parse the boolean from the form string
    just_bool = str(get_justification).lower() == "true"
    print(f"DEBUG: get_justification received as '{get_justification}', interpreted as {just_bool}")
    
    df = pd.read_excel(file.file)
    processed_df = evaluation_service.evaluate_excel_process(df, get_justification=just_bool)
    
    output = io.BytesIO()
    print("Generating Excel output...")
    processed_df.to_excel(output, index=False)
    print("Excel generation completed.")
    output.seek(0)

    from fastapi import Response
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=evaluated_{file.filename}"}
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)