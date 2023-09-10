FROM python:3.11

RUN mkdir BattleshipDocker

WORKDIR BattleshipDocker

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/__main__.py"]
