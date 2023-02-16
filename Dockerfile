FROM python:3.10-slim

WORKDIR /opt/

# EXPOSE 8001

# Enable venv - but is it needed here?
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["python", "runner.py"]
