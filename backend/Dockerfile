# --------- requirements ---------

FROM python:3.12-slim AS requirements-stage

WORKDIR /tmp

RUN pip install poetry poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


# --------- final image build ---------
FROM python:3.12-slim

WORKDIR /home/python/app

COPY --from=requirements-stage /tmp/requirements.txt /home/python/app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /home/python/app/requirements.txt

COPY . /home/python/app/

CMD ["uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
