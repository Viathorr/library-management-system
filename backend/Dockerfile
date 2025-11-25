FROM condaforge/mambaforge:latest

WORKDIR /app

COPY environment.yml .

RUN mamba env create -f environment.yml

SHELL ["bash", "-l", "-c"]
RUN echo "conda activate fastapi-env" >> ~/.bashrc

COPY . .

EXPOSE 8000

CMD ["bash", "-l", "-c", "conda run -n fastapi-env uvicorn app.main:app --host 0.0.0.0 --port 8000"]
