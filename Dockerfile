FROM python:3.8-slim-buster

#ENV VIRTUAL_ENV=/opt/venv
#RUN python3 -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy directories and files
COPY api_pass.txt .
COPY main.py .
COPY etl.py .
COPY currency.py .
ADD input input
# Run the application:
CMD ["python", "main.py"]