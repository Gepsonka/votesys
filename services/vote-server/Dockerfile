FROM python:3.11-alpine

COPY  requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python3", "-m", "flask", "--app", "src/main", "run", "--host=0.0.0.0"]