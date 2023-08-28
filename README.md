# Prueba técnica 

## Resumen:

En este repo encontraras el codigo de un servicio automatizado de inferencia en batch para predecir precios de Farmacos.

Es una solución end-to-end que aborda una estrategia de pipelines:

* **Training Pipeline**: automatiza la extracción, entrenamiento, tracking y despliegue a producción del modelo a traves de un ci/cd pipeline ejecutado desde un trigger de Github Actions.

El modelo se despliega bajo una infraestructura serverless para ser consumido como REST API en online y batch modes.
(Se emplea FastAPI, Docker, AWS ECR, Lambda Functions y API Gateway para el despliegue.)

* **Batch Inference Pipeline**: automatiza la generación de predicciones a partir de un schedule del pipeline de inferencia en Github Actions.

*nota:* todos los pipelines se orquestan con Prefect.

* **(plus) Online Predictions**: Alternativamente se sirve la API en una UI Webapp para permitir realizar predicciones individuales o de carga masiva vía CSV.

## Instrucciones:

A continuación podras encontrar las instrucciones para generar inferencias a partir del modelo entrenado.
Sigue los siguientes pasos:

### 1. Clona el Repositorio

Primero, clona el repo para correr en local:

Deberas tener instalado un IDE para poder ejecutar los scripts. Recomiendo Visual Studio Code.

```bash
git clone https://github.com/DiegoCotacio/drugs_price_prediction.git
```
```bash
📦 drugs_price_prediction
 ┣ 📂 .github/workflows               #Workflow de Github actions para automatizar retraining y batch inference  
 ┃  ┣ 📄 cicd_deployment.yml          # github actions que corre modelo, lo dockeriza, despliega en AWS ECR y lambda.
 ┃  ┣ 📄 batch_inference_service.yml  # github actions que crea schedule para ejecutar periodicamente el inferece batch job
 ┣ 📂 .gitignore
 ┣ 📂 .prueba_tecnica_rurall.egg-info # config para acceder a src como package
 ┣ 📂 data                            # input data y output (contiene el submission output)
 ┣ 📂 notebooks                       # testea scripts
 ┣ 📂 training_reports                # guarda resultados de training para data quality, drift y model evaluation
 ┃
 ┣ 📂 src                             # codigo del proyecto
 ┃ ┃
 ┃ ┣ 📂 components                    # modulos para procesos puntuales:
 ┃ ┃ ┣ 📝 data_ingestion.py           #   ingesta de datos
 ┃ ┃ ┣ 📝 preprocessor.py             #   preprocesamiento de datos
 ┃ ┃ ┣ 📝 hyp_optimizer.py            #   optimizacion de hiperparametros del modelo
 ┃ ┃ ┣ 📝 model_evaluation.py         #   evaluacion del modelo
 ┃ ┃ ┗ 📝 reports.py                  #   reportes de entrenamiento
 ┃ ┃                                   
 ┃ ┣ 📂 pipelines                     # Son los pipelines para inferencia y entrenamiento
 ┃ ┃ ┣ 📝 batch_inference_pipeline.py #   carga datos, genera prediccion y guarda resultados
 ┃ ┃ ┗ 📝 training_pipeline.py        #   carga datos, preprocesa, entrena modelo, evalua y guarda modelo
 ┃ ┣ 📝 __init__.py
 ┃ ┣ 📝 exception.py                  # util
 ┃ ┣ 📝 logger.py                     # util
 ┃ ┗ 📝 utils.py                      # más utils
 ┃
 ┣ 📂 api_artifacts                   # contiene los elementos (modelos y csv) para desplegar la API
 ┣ 📝 app.py                          # API de Fast API con 3 endpoints para generar inferencias
 ┣ 📝 api_utils.py                    # utils de la API
 ┣ 📦 Dockerfile                      # Docker image para desplegar a AWS ECR y consumir en Lambda Function
 ┣ 📂 requirements.txt                # requerimientos del proyecto
 ┗ 🐍 streamlit_app.py                # Webapp para interactuar con 2 endpoints de la API
 ┣ 📄 README.md
 ┗ 📝 setup.py
```

### 2. Instala las dependencias

Antes de instalar las librerias te recomiendo crear un entorno virtual y activarlo.
Puede usar **python -m venv env** para Windows.

```bash
pip install -r requirements.txt
```

### 3. Genera predicciones


El repo ya cuenta con un modelo entrenado, empaquetado en una API y desplegado en una Imagen Docker en AWS ECR y servido en una Lambda Function. Ejecuta el siguiente comando para generar las predicciones en el archivo drugs_test.csv. En el folder "/data" podras encontrar los resultados en el archivo "prediction_outputs.csv"


```bash
python src/pipelines/batch_inference_pipeline.py
```

Tambien puedes generar predicciones a partir de una Webapp simple construida en Streamlit para hacer predicciones online.
Ejecuta el siguiente comando:

```bash
streamlit run streamlit_app.py
```

1. En la opción "Online", selecciona los valores que desees y presiona el botón de "Estimar precio del farmaco".

2. Para la opción de "Batch", carga el archivo ui_test.csv desde la carpeta "/data da click en "Estimar precio del farmaco".


### 4. Reentrena un nuevo modelo a traves de un pipeline de reentrenamiento 

Puedes reentrenar un nuevo modelo a partir de un pipeline de reentrenamiento que retorna, ademas del modelo reentrenado, reportes de calidad de datos, drift, y evaluación a profundidad del modelo. De igual forma trackea todas las metricas y artefactos en MLFlow.

Ejecuta el siguiente codigo para entrenar un nuevo modelo.

*Nota*: Si quieres realizar predicciones con este nuevo modelo, debes marcar las url de AWS y desmarcar las rutas locales 


```bash
python src/pipelines/training_pipeline.py
```

Tanto las metricas, el modelo y los reportes se envian a MLFlow local.
Para ver los artefactos y metricas en MLFlow local ejecuta:

```bash
mlflow ui
```
Si deseas probar el modelo desde la API de Fast API en loca, puedes ejecutar el siguiente comando y abrir url en /docs:

```bash
uvicorn app:app --reload
```

Con esto podras probar el modelo reentrenado en los endpoints de Streamlit o en batch predictions desmarcando primero los # de local y marcando las URL.

## Comentarios:

Dado que para el despliegue en prod se requieren de multiples credenciales (API Keys de AWS, Prefect, data sources y Dagshub), los archivos .py que se sugierieron ejecutar son versiones simplificadas para correr en local de los pipelines diseñados para producción. Los archivos principales son mlops_retraining_job.py y mlops_batch_inference_job.py, los cuales se configuran en los .yml de Github Actions para ser automaticamente ejecutados.



