FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	default-mysql-client \
	curl \
	&& rm -rf /var/lib/apt/lists/*

#непривилегированный пользователь
RUN useradd -m -u 1000 appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
	CMD curl -s -o /dev/null http://localhost:8000/login/ || exit 1

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
