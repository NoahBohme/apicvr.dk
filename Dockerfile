# 
FROM python:3.13-slim

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

RUN python -m pip install --upgrade pip

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./ /code/app

COPY ./apis /code/apis

COPY ./frontend /code/frontend

COPY ./backend /code/backend

COPY ./modules /code/modules

# Copy .env
COPY .env /code/.env

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3450"]
