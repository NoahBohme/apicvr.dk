# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./ /code/app

COPY ./apis /code/apis

COPY ./frontend /code/frontend



# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3450"]
