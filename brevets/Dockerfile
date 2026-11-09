FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod 644 *.py
EXPOSE 5000
ENTRYPOINT ["python", "-B"]
CMD ["flask_brevets.py"]
