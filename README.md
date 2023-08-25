# Prueba técnica 

Hola, acontinuación podras encontrar las instrucciones para generar inferencias a partir del modelo entrenado.
Sigue los siguientes pasos:

### 1. Clona el Repositorio

Primero, clona este repositorio en tu máquina local utilizando el siguiente comando:

```bash
git clone https://github.com/DiegoCotacio/drugs_price_prediction.git
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3. Genera predicciones

El repo ya cuenta con un modelo entrenado, empaquetado en una API y desplegado en una Imagen Docker en AWS ECR y servido en una Lambda. Ejecuta el siguiente comando para generar las predicciones en el archivo drugs_test.csv. En el folder "/data" 
podras encontrar los resultados en el archivo "prediction_outputs.csv"


```bash
python src/pipelines/batch_inference_pipeline.py
```

Tambien puedes generar predicciones a partir de una Webapp simple construida en Streamlit para hacer predicciones online.
Ejecuta el siguiente comando:

```bash
streamlit run streamlit_app.py
```

1. En la primera página de la aplicación, selecciona los valores que desees y presiona el botón de "Predecir Precios".

2. Para la opción de "Batch", carga el archivo ui_test.csv desde la carpeta "/data da click en "Predecir precios".


### Reentrena un nuevo modelo a traves de un pipeline de reentrenamiento 

Puedes reentrenar un nuevo modelo a partir de un pipelie de entrenamiento que retorna, ademas del modelo reentrenado, el 
pipeline retorna reportes de calidad de datos, drift, y evaluación a profundidad del modelo. De igual forma trackea todas 
las metricas y artefactos en MLFlow.

Ejecuta el siguiente codigo para entrenar un nuevo modelo.
Si quieres realizar predicciones con este nuevo modelo, debe cambiar el url del ENPOINT por 


```bash
python src/pipelines/training_pipeline.py
```

Para ver los artefactos y metricas en MLFlow local ejecuta:

```bash
mlflow ui
```