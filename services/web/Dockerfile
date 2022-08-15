# pull official base image
FROM ubuntu:20.04


# set work directory
WORKDIR /usr/src/app

RUN apt update; apt upgrade -y
RUN apt install -y python3 python3-flask python3-flask-sqlalchemy python3-pip \
                python3-flask-httpauth python3-passlib python3-psycopg2 \
		python3-gunicorn netcat-openbsd gunicorn

# create the app user
RUN adduser --system --group taskfarm

# install dependencies
COPY ./entrypoint.sh /usr/src/app/
#RUN pip install -r requirements.txt
RUN pip install taskfarm

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]