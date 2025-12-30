ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-alpine3.23

WORKDIR /tests

ARG TARGETPLATFORM

RUN apk add --no-cache python3 py-pip curl uv

RUN python3 -m venv /venv

COPY requirements.txt .
RUN uv pip sync -p /venv/bin/python3 requirements.txt

CMD ["sh -c \"trap : TERM INT; sleep 604800 & wait\""]
