# ✅ Use official Python image
FROM python:3.10-slim

# ✅ Set working directory inside container
WORKDIR /app

# ✅ Copy requirements file first
COPY requirements.txt .

# ✅ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy entire project code
COPY . .

# ✅ Expose port (FastAPI default)
EXPOSE 8000

# ✅ Run FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]