FROM public.ecr.aws/lambda/python:3.10

WORKDIR ${LAMBDA_TASK_ROOT}

COPY api_artifacts ./api_artifacts

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --target .

COPY app.py .
COPY api_utils.py .

CMD [ "app.handler" ]