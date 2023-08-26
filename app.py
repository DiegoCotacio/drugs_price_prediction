
import os
from typing import List, Dict
import logging

from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import(
    HTMLResponse,
    JSONResponse,
    Response,
    FileResponse
)
import uvicorn
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from mangum import Mangum

import numpy as np
import pandas as pd
from api_utils import Preprocessor, load_object



app = FastAPI()
handler = Mangum(app)


"""
Out API contains 3 endpoints, each one for 3 deployment variations:

1. Online Service for 
2. Online
3. Batch Inference Service

"""


# ------- Upload artifacts

#model
model_path = os.path.join("api_artifacts", "model.pkl")
model = load_object(file_path= model_path)



class Features(BaseModel):
    drug_id: str
    description: str
    administrative_status: str
    marketing_status: str
    approved_for_hospital_use: str
    reimbursement_rate: str
    dosage_form: str
    route_of_administration: str
    marketing_authorization_status: str
    marketing_declaration_date: int
    marketing_authorization_date: int
    marketing_authorization_process: str
    pharmaceutical_companies: str
    

@app.get('/')
def index() -> HTMLResponse:
    return HTMLResponse('<h1><i> Rurall - API Endpoints </i></h1>')


#-------------------------- Endpoint 1. Online prediction

@app.post("/online_predict")
async def predict(
    response: Response,
    features_item: Features,
    ) -> JSONResponse:

    try:
        #input_dict = jsonable_encoder(input_data)
        input_dict = features_item.dict()
        input_df = pd.DataFrame([input_dict])
        original_row = input_df.copy()

        preprocessor = Preprocessor()
        input_df = preprocessor.preprocess_dataframe(input_df)
        
        #generate predictions
        prediction = model.predict(input_df)[0].item()
        original_row['prediction'] = prediction

        # Devuelve un objeto JSON con la clave "prediction"
        response_data = {'prediction': prediction}
        return JSONResponse(content=response_data)

        #return prediction

    except Exception as e:
        response.status_code = 500
        logging.error(e, exc_info=True)
        return JSONResponse(content={'error_msg': str(e)})
    



#-------------------------- Endpoint 2. Online prediction for uploaded csv

@app.post("/online_batch_predict")
async def batch_predict(file: UploadFile,response: Response):

    try:
        
        input_df = pd.read_csv(file.file)
        # Crear una copia de los datos iniciales para preservarlos
        original_df = input_df.copy()
        
        preprocessor = Preprocessor()
        input_df_proc = preprocessor.preprocess_dataframe(input_df)
        
        # Realizar la predicción utilizando los datos preprocesados
        predictions = model.predict(input_df_proc)
        
        # Agregar la etiqueta de predicción a los datos iniciales
        original_df['prediction'] = predictions
        
        return original_df.to_dict(orient='records')
    
    except Exception as e:
        response.status_code = 500
        logging.error(e, exc_info=True)
        return JSONResponse(content={'error_msg': str(e)})


#-------------------------- Endpoint 2. Batch Inference Service

@app.post("/batch_predict_pipeline")
async def batch_inference_pipeline(input_list: List[Features],response: Response):

    try:
        
        output_list = [input_data.dict() for input_data in input_list]
        input_df = pd.DataFrame(output_list)
        
        original_df = input_df.copy()
        preprocessor = Preprocessor()
        input_df_proc = preprocessor.preprocess_dataframe(input_df)
        
        predictions  = model.predict(input_df_proc)
        
        # Agregar la etiqueta de predicción a los datos iniciales
        original_df['prediction'] = predictions
        prediction_list = original_df.to_dict(orient='records')
        
        return prediction_list
    
    except Exception as e:
        response.status_code = 500
        logging.error(e, exc_info=True)
        return JSONResponse(content={'error_msg': str(e)})



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)