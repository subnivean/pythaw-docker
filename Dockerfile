FROM python:3.9

COPY requirements.txt .

RUN python -mpip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# `/app` is mounted to the `src` dir in the
# `docker run` command.
WORKDIR /app
RUN mkdir /data

CMD ["python", "checktemp.py"]
