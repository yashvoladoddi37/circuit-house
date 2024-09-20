
# Content-Recommendation-Poc
Personalised recommender systems for dynamic genres

## Setup

1. Clone the repository.
   ```
   git pull origin <your-branch-name>
   ```
3. Create a Virtual environment to run the code.
   ```
   python -m venv venv --prompt <env name>
   ```
5. Activate Virtual environment.
   ```
    source venv/bin/activate
   ```
7. Install the dependencies.
   ```
    pip install -r requirements.txt
   ```
9. Set Up Your Datasets.
    ```
    https://drive.google.com/drive/folders/1NwBGYC6RR5iHmgHVSU603Ptn0-MHnAe7?usp=sharing
    ```
11. Run the Application.
      ```
       uvicorn app.main:app --reload
      ```


## Requirements

- Python 3.9
- FastAPI
- Uvicorn
- pandas
- numpy
- scikit-learn
- nltk
- surprise
