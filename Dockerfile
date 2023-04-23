FROM python:3.10

WORKDIR /code/

COPY ./requirements_ccalc.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements_ccalc.txt

COPY . ./

CMD python3 ccalc.py
