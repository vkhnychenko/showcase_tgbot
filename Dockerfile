FROM python:3.8

WORKDIR /bot

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

CMD ["python", "app.py"]