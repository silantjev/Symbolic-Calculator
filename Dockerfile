FROM python:3.10

WORKDIR /code/

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . ./

CMD python3 ccalc.py
