FROM tiangolo/uwsgi-nginx-flask:python3.8
COPY ./requirments.txt /var/requirments/requirments.txt
RUN pip install -r /var/requirments/requirments.txt
COPY ./app /app
