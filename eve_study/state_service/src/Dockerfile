FROM python:2.7
WORKDIR /src
ADD requirements.txt /src/
RUN pip install -r requirements.txt
ADD *.py /src/
ADD ilo/*.py /src/ilo/
ADD client/*.py /src/client/
