import pandas as pd
import requests
from datetime import datetime
from prefect import flow, task
import logging



# ------------------------ -EXTRACT DATA:

#@task
#def extract_dataframe_from_bigquery(project_id, dataset_extract_id, table_extract_id) -> pd.DataFrame:  
   
 #  """ Función que realiza una conexion a una tabla de BQ y extrae todos los datos del dia actual """
   
 #  try:
  #     client = connect_to_bigquery()
   #    current_date = datetime.now().strftime("%Y-%m-%d") 
    #   query = f"SELECT * FROM `{project_id}.{dataset_extract_id}.{table_extract_id}` WHERE DATE_TRUNC(date, DAY) = '{current_date}'" 
     #  df = client.query(query).to_dataframe() 
      # return df
   
#   except Exception as e:
 #       logging.error(e)
  #      raise e
   
def load_input_data():

    test_path = "data/drugs_test.csv"
    try:
        # Cargar el CSV en un DataFrame de pandas
        df = pd.read_csv(test_path)

        return df
    
    except FileNotFoundError:
        print("El archivo CSV no se encontró en la ubicación especificada.")
        
        return None
  
#-------------------------- GENERATE PREDICTIONS

#@task
def generate_batch_predictions(df: pd.DataFrame) -> pd.DataFrame:

    """ Crea copia del df original, pasa datos al endpoint en JSON (dict list), recupera predicciones y las une al df original """

    try:
        input_df = df
        input_list = input_df.to_dict(orient='records')
        
        #API_ENDPOINT = "http://127.0.0.1:8000/batch_predict_pipeline"
        API_ENDPOINT = "https://jjnw2oyoolgt4dp7cxbh2cmbyu0bjpzf.lambda-url.us-east-2.on.aws/batch_predict_pipeline"

        
        response = requests.post(API_ENDPOINT, json=input_list)
        
        if response.status_code == 200:
             predictions_output = response.json()
             predictions_df = pd.DataFrame(predictions_output)
        else:
             print("Error al realizar las estimaciones") 

        return predictions_df
    
    except Exception as e:
        logging.error(e)
        raise e
    
#------------------------- LOAD PREDICTIONS


def save_predictions(df, file_name, folder_name):
    
    # Formating output
    columnas_deseadas = ["drug_id", "prediction"]
    df= df[columnas_deseadas]
    
    # Guardar el DataFrame filtrado en un archivo CSV dentro de la carpeta especificada
    output_path = f"{folder_name}/{file_name}.csv"
    try:
        df.to_csv(output_path, index=False)
        print(f"Resultados guardados exitosamente en {output_path}.")
    
    except Exception as e:
        print("Error al guardar el DataFrame filtrado:", e)
        

#@task
#def save_predictions_to_bigquery(df_final: pd.DataFrame,
#                                 table_export_id: str,
#                                 dataset_export_id: str):

#    try:
    
#        client = connect_to_bigquery()
#        table_ref = client.dataset(dataset_export_id).table(table_export_id)
#        table_exists = client.get_table(table_ref) 

#        if table_exists is None: 
#           schema = []
#           for column_name, column_type in df_final.dtypes.items():
#               schema.append(bigquery.SchemaField(name=column_name, field_type=column_type.name))

#        table = bigquery.Table(table_ref, schema=schema)
#        table = client.create_table(table)
#        print(f"Se ha creado la tabla {dataset_export_id}.{table_export_id} en BigQuery.")

#        job_config = bigquery.LoadJobConfig()
#        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
#        job = client.load_table_from_dataframe(df_final, table_ref, job_config=job_config)
#        job.result()

#    except Exception as e:
#        logging.error(e)
#        raise e
    
#------------------------- EPL PIPELINE

#@flow(name="Drugs prices batch inference pipeline")
def run_batch_predictions_pipeline():
    try:
        df = load_input_data()
        
        df_final = generate_batch_predictions(df)

        file_name= 'prediction_output'
        folder_name = 'data'
        
        load_completed = save_predictions(df_final, file_name, folder_name)
        
        return load_completed
    
    except Exception as e:
        logging.error(e)
        raise e

#------------------------ RUN BATCH PREDICTION PIPELINE

if __name__ == '__main__':
    run_batch_predictions_pipeline()
