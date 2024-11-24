FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/

ENV POETRY_VIRTUALENVS_CREATE=false


RUN poetry lock &&\
    poetry install && \
    poetry build && \
    pip install dist/*.whl

CMD ["pytest", "tests/"]