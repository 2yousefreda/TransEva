import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.model.gemini_3_flash import Gemini3Flash
from app.service.evaluation_service import EvaluationService

app = FastAPI()

llm_model = Gemini3Flash(settings.GEMINI_API_KEY, settings.GEMINI_MODEL_NAME)
evaluation_service = EvaluationService(llm_model)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/evaluate")
def evaluate_excel(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)
    processed_df = evaluation_service.evaluate_excel_process(df)
    
    output = io.BytesIO()
    processed_df.to_excel(output, index=False)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=output.xlsx"}
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="[IP_ADDRESS]", port=8000)