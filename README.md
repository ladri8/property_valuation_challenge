# Property Valuation ML Pipeline


## Executive Summary

This repository contains a modular, scalable ML solution for property valuation in Chile. It features a training pipeline, a FastAPI-based prediction service, and Dockerized deployment, all designed with future database extensibility and with evolving business and infra needs.

---

## Approach : Modular Pipeline and Productization

The focus of this project was to productize a notebook-based solution. All code was modularized into reusable Python functions, organized into `src/` modules, composed into a Prefect `main_flow.py` script. The pipeline that trains the model and the API that serves predictions can be run sequentially using docker compose. 

The full ochestrated pipeline:
- Performs data validation using Pandera
- Trains and evaluates a regression model
- Saves the trained model as a `.joblib` file
- Serves predictions via a FastAPI endpoint

To improve maintainability, I replaced the hardcoded values in the notebook with a more centralized configuration system using `pydantic_settings.BaseSettings`. This makes it easier to manage paths, features, targets, api keys via .env, and hyperparameters via a sahred `config.py`

Pipeline Flow: 

train.csv → data validation → preprocessing → model training → evaluation → model.joblib → served via FastAPI

---

## Project Structure



Project layout (excluding notebooks and metadata):

```bash
├── src/                  # Python modules and core logic
├── api/                  # FastAPI entrypoint and utilities
├── models/               # Trained model artifacts
├── data/                 # Input data (CSVs)
├── examples/             # Sample inputs for API
├── Dockerfile.*          # Dockerfiles for API and pipeline
├── docker-compose.yml    # Orchestrates multi-container setup
├── requirements.txt      # Runtime dependencies
├── environment.yml       # Conda environment
├── README.md             # Project documentation
```
---

## Dependencies and Usage

I used Conda for environemt and package management. 
To set up the development environment:

```bash
conda env create -f environment.yml
conda activate property-val-env
```

ℹ️ Data Note:
Since the data is not included in the github repo for privacy issues, 
Place both `train.csv` and `test.csv` in the `/data` folder at the top of `property_valuation`. 

Once that is done, to run only the model train and evaluation parts do:

```bash
python src/main_flow.py
```

Or to run the entire orchestrated pipeline (model + API) use: 

```bash
docker compose build --no-cache
docker compose up
```

API: Here's an example on how to test the API once running. I also provided a full json example in the examples directory. 

```bash
curl -X POST "http://localhost:8000/predict" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <your_api_key>" \
    -d '{"feature_1": value1, "feature_2": value2, ...}'
```

Security Note:
The API uses a basic token-based authentication system. You have to provide the API_KEY via the .env file and include it in the request header as a Bearer token.

I placed an example .env file here in the repo where the correct api key needs to go

```bash
    cp .env.example .env
```

--- 

## Assumptions and Areas of Improvement

1. Data Preparation and Validation:
The current model assumes minimal preprocessing. However, real-world pipelines benefit from rigorous data cleaning, handling of missing values and outliers, and standardization of numeric features. Additionally, using a separate validation dataset (in addition to train/test splits) would enable better hyperparameter tuning and help detect overfitting early in the pipeline.

2. Schema Enforcement and Stability:
I added a Pandera-based validation step to ensure basic schema consistency. While it's not fully enforced to preserve the original notebook structure, this step helps detect shifts in feature distributions over time. More robust schema enforcement — potentially using tools like Weights & Biases — would improve model stability as data evolves.

3.  Data Versioning:
A step of data versioning with tools like DVC, will also benefit the pipeline as things scale. So the datasets and the changes are kept 

4. Model Experimentation and Selection: 	
Based on the principle of no-free lunch, the pipeline could also test different regressors/models and different hyperparameters. This could be easily integrated into MLFlow, saving models and metrics, and then selecting the best model in a more programmatic way.  This becomes even more important when there is continuous data streaming into the pipeline. 

5.	Model Interpretability: 
The client can benefit from a SHAP explainer graph (i.e. swarm plot) to understand which features are driving prices globally and locally. This step makes pipelines more interpretable and also provides smoke tests to understand whether the product makes real-world sense, building trust with the client.  

6.	API Input Validation:
The API , as is, doesn't currently enforce input formats. With a few Pydantic classes this can be accomplished so it has a more robust handling of the incoming request data. 

7. Monitoring for Data Drift:
After deployment, it's critical to monitor data drift — changes in input distributions that can silently degrade model performance. Detecting drift enables automated retraining or rollback to previous model versions. This monitoring could be enhanced using tools like Prometheus and Grafana for observability.

8.	Database Abstraction and Extensibility:
Since the prompt mentions possible databases, the database abtraction is general, but could be implemented using oop, which could make this more extensible or clear. 

9.	Retraining Strategy:
The pipeline currently retrains the model each time the container starts, which may be inefficient in production. A better approach would involve a scheduled retraining cadence (e.g., nightly or weekly), or triggering retraining in response to detected data drift — especially useful in fast-changing markets like real estate.

10.	CI/CD and Testing Coverage
With more time, a more robust CI/CD pipeline with more tests, especially for the most input dependent portions and also to validate data types and input and output formats. There is error handling in some places but this can be made more robust in a future iteration. 

11. Note on the micromamba Docker builds: 
The docker builds are with micromamba instead of conda (the original dev environment), which reduces build time and complexity at container build.

12. Note on API-key Use:
The API uses a simple token-based authentication system, where the API key is loaded from environment variables using pydantic_settings.BaseSettings. When running with Docker Compose, the .env file is automatically passed into the container, making the key accessible to the app without hardcoding.

