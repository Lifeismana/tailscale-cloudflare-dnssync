FROM python:3.15-slim
WORKDIR /app
ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "app.py", "--repeat"]
