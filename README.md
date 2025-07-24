# Property Valuation ML Pipeline


## Executive Summary

This repository contains a modular, scalable ML solution for property valuation in Chile. It features a training pipeline, a FastAPI-based prediction service, and Dockerized deployment, all designed with future database extensibility and business alignment in mind.

---

## Approach : Modular Pipeline and Productization

The focus of this project was to productize a notebook-based solution. All code was modularized into reusable Python functions, organized into `src/` modules, composed into a Prefect `main_flow.py` script. The pipeline that trains the model and the api that serves can be run sequentially using docker compose. 

The full ochestrated pipeline:
- Performs data validation using Pandera
- Trains and evaluates a regression model
- Saves the trained model as a `.joblib` file
- Serves predictions via a FastAPI endpoint

To improve maintainability, I removed hardcoded values and replaced them with a centralized configuration system using `pydantic_settings.BaseSettings`. This allows management of paths, features, targets, and hyperparameters via `config.py` in the shared directory.

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
--

## Dependencies and Usage

I used Conda for environemt and package management. 
To set up the development environment:

```bash
conda env create -f environment.yml
conda activate property-val-env
```

Note on the data files:
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

1.	The model could be improved  with a robust data cleaning and feature engineering step. The assumption here was that the model as is in the notebook was good enough, but in real practice this step is crucial. Numeric features need to be standardized or normalized, and there needs to be handling of NA’s and outliers. This to avoid bias in predictions. And though the regressor selected in this case is robust to data issues, it is still worth it to test different models with different data handling strategies.

2.  A data schema validation will also improve the pipeline. I used a pandera data validation step here, though not fully enforced, as to not completely change the model, but this step helps in the future to make the pipeline more robust in case new features come in or even the existing features potentially with a new range of values. This change in data values or distribution can degrade models overtime, so it is useful to develop pipelines that are robust and pick up on such changes.  A more strict way of enforcing data schema validation could be done with the package WeightandBiases.

3.  A step of data versioning with tools like DVC, will also benefit the pipeline as things scale. So the datasets and the changes are kept 

4.	Based on the principle of no-free lunch, the pipeline could also test different regressors/models and different hyperparameters. This could be easily integrated into MLFlow, saving models and metrics, and then selecting the best model in a more programmatic way.  This becomes even more important when there is continuous data streaming into the pipeline. 

5.	Currently the model is evaluated using only the training and test sets, but adding a validation dataset would allow for better model selection and tuning by helping to detect and mitigate overfitting. 

6.	The client can benefit from a SHAP explainer graph (i.e. swarm plot) to understand which features are driving prices globally and locally. This step makes pipelines more interpretable and also provides smoke tests to understand whether the product makes real-world sense, building trust with the client.  

7.	The API , as is, doesn't currently enforce input formats. With a few Pydantic classes this can be accomplished so it has a more robust handling of the incoming request data. 

8.	After models are put in production and are being actively serving, a data drift step needs to be put in place so models that are degrading can be rolled-back and retrain steps can occur so models learn from the new data and can better predict in a constant data landscape. This could benefit from integration with tools like Prometheus and Grafana.  

9.	Since the prompt mentions possible databases, the database abtraction is general, but could be implemented using oop, which could make this more extensible or clear. 

10.	Model retraining: The pipeline as is retrains on container starts each time the container starts, but this may not be as efficient for future client needs. This could be improved by using a scheduler to retrain the model based on needs. As is, this is a batch-type problem, there could be a nighlty or weekly model retrain or retrain events triggered based on datadrift, especially in market where property values are changing fast. 

11.	With more time, a more robust CI/CD pipeline with more tests, especially for the most input dependent portions and also to validate data types and input and output formats. There is error handling in some places but this can be made more robust in a future iteration. 

12. The docker builds are with micromamba instead of conda (the original dev environment), which reduces build time and complexity at container build. 
