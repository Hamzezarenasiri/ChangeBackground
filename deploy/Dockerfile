FROM python:3.11.4-slim-bullseye as prod


RUN apt-get update \
&& apt-get install libgl1-mesa-glx libgl1-mesa-dev libglib2.0-0 -y \
&& apt-get clean
RUN pip install poetry==1.4.2

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN poetry install --only main

# Copying actuall application
COPY . /app/src/
RUN poetry install --only main

CMD ["/usr/local/bin/python", "-m", "background_changer"]

FROM prod as dev

RUN poetry install
