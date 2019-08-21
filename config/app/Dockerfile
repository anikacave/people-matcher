FROM python:3.7

RUN pip install numpy pandas geopy flask
RUN pip install dash==1.0.0 \
    dash_table==4.0.0 \
    plotly==4.0.0 \
    dash-core-components==1.0.0 \
    dash-html-components==1.0.0 \
    dash-renderer==1.0.0 \
    dash-bootstrap-components==0.6.3
RUN pip install psycopg2 pytest sqlalchemy
RUN pip install celery==4.3.0 redis==3.3.8
WORKDIR /app
