FROM python:3.10-slim

WORKDIR /app

# ✅ Install certificates (FIX)
RUN apt-get update && apt-get install -y ca-certificates

# ✅ Upgrade pip safely
RUN pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Copy requirements
COPY requirements.txt .

# ✅ Install dependencies with trusted hosts
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]