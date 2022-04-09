# start by pulling the python image
FROM python:3.8

# copy the requirements file into the image
COPY ./requirement.txt /Loss_Assessment_Processing/requirement.txt

# switch working directory
WORKDIR /Loss_Assessment_Processing

# install the dependencies and packages in the requirements file
RUN pip install -r requirement.txt

# copy every content from the local file to the image
COPY . /Loss_Assessment_Processing

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["python main.py" ]