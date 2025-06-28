FROM --platform=linux/amd64 python:3.10 as builder
RUN pip install llama-cpp-python --no-cache-dir

FROM --platform=linux/amd64 python:3.10-slim
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "src.api_server:app", "--host", "0.0.0.0"]
