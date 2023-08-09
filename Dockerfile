FROM python:3.10.11

WORKDIR /app
COPY . .


RUN pip3 install dojo-compass
RUN npm install --save-dev hardhat

CMD ["python3", "run.py"]