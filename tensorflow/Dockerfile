FROM tensorflow/tensorflow:latest-py3
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip
COPY . .
CMD ["python3", "app.py"]
