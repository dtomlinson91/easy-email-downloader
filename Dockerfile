FROM python:3.8-alpine

RUN mkdir /app
WORKDIR /app

# Copy poetry requirements
COPY ["pyproject.toml", "poetry.lock", "./"]

# Install the environment
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Copy codebase in
COPY ["easy_email_downloader", "./"]
