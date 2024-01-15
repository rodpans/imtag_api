FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY /app .

EXPOSE 80

CMD ["python","app.py"]
