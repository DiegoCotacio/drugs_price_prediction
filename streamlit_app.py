import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import json

# Desmarcar para realizar predicciones con el modelo reentrenado (marca las URL de AWS)
#PREDICT_ENDPOINT = 'http://127.0.0.1:8000/online_predict'
#BATCH_PREDICT_ENDPOINT = 'http://127.0.0.1:8000/online_batch_predict'

PREDICT_ENDPOINT = 'https://jjnw2oyoolgt4dp7cxbh2cmbyu0bjpzf.lambda-url.us-east-2.on.aws/online_predict'
BATCH_PREDICT_ENDPOINT = 'https://jjnw2oyoolgt4dp7cxbh2cmbyu0bjpzf.lambda-url.us-east-2.on.aws/online_batch_predict'


def predict_input(input_data):
    response = requests.post(PREDICT_ENDPOINT, json=input_data)
    
    if response.status_code == 200:
        response_data = response.json()
        if 'prediction' in response_data:
            return response_data['prediction']
        else:
            print("La clave 'prediction' no está presente en la respuesta JSON")
            return None
    else:
        print("Error al obtener una estimación de la API")
        return None
    
def run():
    #Instanciar las imagenes
    #from PIL import Image
    #image = Image.open('logo.png')
    #image_hospital = Image.open('hospital.jpg')

    # Iniciar el codigo de la app
    #st.image(image, use_column_width= False)
    
    add_selectbox =  st.sidebar.selectbox(
        "Indica un metodo para realizar predicciones",
        ("Online", "Batch"))
    
    st.sidebar.info("UI para predecir Precios de Farmacos")
    st.sidebar.success("")
    #st.sidebar.image(image_hospital)

# ------ ONLINE PREDICTION

    if add_selectbox == "Online":

        drug_id= st.selectbox("drug_id",["1_test","2_test","9_test", "14_test", "12_test", "10_test"])

        description = st.selectbox("description", ["plaquette(s) thermoformée(s) PVC PVDC aluminium de 30 comprimé(s)",
                                                    "plaquette(s) thermoformée(s) PVC PVDC aluminium de 90 comprimé(s)",
                                                    "plaquette(s) thermoformée(s) PVC-Aluminium de 30 comprimé(s)",
                                                    "plaquette(s) thermoformée(s) aluminium de 90 comprimé(s)",
                                                    "1 seringue(s) préremplie(s) en verre de 20  ml"])
        
        administrative_status = st.selectbox("administrative_status", ["Présentation active", "Présentation abrogée"])

        marketing_status = st.selectbox("marketing_status", ["Déclaration d'arrêt de commercialisation",
                                                                "Déclaration de commercialisation","Arrêt de commercialisation (le médicament n'a plus d'autorisation)"])
        approved_for_hospital_use = st.selectbox("approved_for_hospital_use", ["non", "oui"])

        reimbursement_rate = st.selectbox("reimbursement_rate", ["65%", "30%", "15%", "100%"])

        dosage_form = st.selectbox("dosage_form", ["comprimé pelliculé", "comprimé sécable", "comprimé", "gélule"])

        route_of_administration = st.selectbox("route_of_administration", ["orale", "intraveineuse", "cutanée", "ophtalmique","intramusculaire"])
        
        marketing_authorization_status =st.selectbox("marketing_authorization_status",["Autorisation active", "Autorisation abrogée", "Autorisation archivée",
                                           "Autorisation retirée","Autorisation suspendue"])
        
        marketing_declaration_date = st.selectbox("marketing_declaration_date",[20130101,20120101,20110101,20140101,20020101,
                                                                       20060101,20070101,20150101,20090101,20050101,20040101])
        
        marketing_authorization_date = st.selectbox("marketing_authorization_date",[20080101,19970101,20060101,20000101,20110101,20130101,
                                                                        20020101,19930101,20010101,20150101,20040101,20100101,19940101])
        
        marketing_authorization_process = st.selectbox("marketing_authorization_process",["Procédure de reconnaissance mutuelle","Procédure nationale",
                                               "Procédure centralisée","Procédure décentralisée","Autorisation d'importation parallèle"])
        
        pharmaceutical_companies = st.selectbox("pharmaceutical_companies", [" TEVA SANTE", " SANOFI AVENTIS FRANCE", " MYLAN SAS", " BIOGARAN",
                                    " EG LABO - LABORATOIRES EUROGENERICS"])

        input_data = {
            'drug_id': drug_id, 
            'description': description,
            'administrative_status': administrative_status,
            'marketing_status': marketing_status,
            'approved_for_hospital_use': approved_for_hospital_use,
            'reimbursement_rate': reimbursement_rate,
            'dosage_form': dosage_form,
            'route_of_administration': route_of_administration,
            'marketing_authorization_status': marketing_authorization_status,
            'marketing_declaration_date': marketing_declaration_date,
            'marketing_authorization_date':  marketing_authorization_date,
            'marketing_authorization_process': marketing_authorization_process,
            'pharmaceutical_companies': pharmaceutical_companies,
            }

        if st.button("Estimar precio del farmaco"):
            output = predict_input(input_data)
            if output is None:
                st.error('Error al obtener una estimacion de la API')
            else: 
                output = '$'+str(output)
                st.success('El valor estimado es de {}'.format(output))
        

# ------ ONLINE BATCH PREDICTION

    if add_selectbox == 'Batch':
        file_upload = st.file_uploader("Cargue un archivo csv para realizar estimaciones", type=['csv'])

        if file_upload is not None:
            if st.button('Estimar precio del farmaco'):

             response = requests.post(BATCH_PREDICT_ENDPOINT, files={'file': file_upload})
             if response.status_code == 200:
                 data = response.json()
                 df = pd.DataFrame(data)
                 st.write(df)
             else:
                 st.write("Error al realizar las estimaciones")

if __name__ == '__main__':
    run()