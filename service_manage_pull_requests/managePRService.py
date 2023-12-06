from fastapi import FastAPI
import uvicorn
import boto3
import requests
from typing import List
import zulu
import datetime
import dateutil
import dateutil.relativedelta

app = FastAPI()

api_token = "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"

#dynamodb
# secret_name = "<SECRET_NAME>"
# region_name = "<aws-region>"
# session = boto3.Session(region_name=region_name)
# # get_s = session.get_secret_value(SecretId = secret_name)

# dynamodb = session.resource('dynamodb')
# table_name = '<table_name>'
# table = dynamodb.Table(table_name)

@app.get("/")
async def index():
    return {"message": "Managing the Pull Requests"}

@app.get("/pulls")
async def retrive_user_issues(contributer:str, organization:str, repo: str):
  #   Issues url can also be taken to obtain Pull Requests
  URL = f"https://api.github.com/repos/{organization}/{repo}/issues"

  try:
    duration_year  = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(years=1))).split('.')[0]
    duration_month = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=1))).split('.')[0]
    duration_week  = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(weeks=1))).split('.')[0]

    valid_contributer = False

    pr_url_year  = f"{URL}?creator={contributer}&since={duration_year}&pulls=true&state=all"
    pr_url_month = f"{URL}?creator={contributer}&since={duration_month}&pulls=true&state=all"
    pr_url_week  = f"{URL}?creator={contributer}&since={duration_week}&pulls=true&state=all"

    print(issues_url_month)

    response_year = requests.get(pr_url_year, headers={"Authorization": 'token %s' % api_token})
    response_month = requests.get(pr_url_month, headers={"Authorization": 'token %s' % api_token})
    response_week = requests.get(pr_url_week, headers={"Authorization": 'token %s' % api_token})

    print(response_month.json())

    if response_year.status_code == 200 and response_month.status_code == 200 and response_week.status_code == 200:
        num_prs_created_year  = len(response_year.json())
        num_prs_created_month = len(response_month.json())
        num_prs_created_week  = len(response_week.json())

        final_statistics = {
          "contributor" : contributer,
          "periodical_statistics":{
            "week":{
                "prs_created": num_prs_created_week,
            },
            "month":{
                "prs_created": num_prs_created_month,
            },
            "year":{
                "prs_created": num_prs_created_year,
            }
          }
        }
        return final_statistics

    elif response.status_code == 202:
        return "Please Try Again!"
    else:
        return "Request Failed!"
  except requests.exceptions.RequestException as exp:
      return f"Error Occured when fetching commits: {exp}"


@app.get('/contributors')
async def retrive_all_contributors(organization:str, repo:str):

    URL = f"https://api.github.com/repos/{organization}/{repo}/stats/contributors"
    response = requests.get(URL, headers={"Authorization": 'token %s' % api_token})
    if response.status_code == 200:
      return response.json()
    else:
      return "Request Failed!"


if __name__ == "__main__":
  uvicorn.run(app, host= "127.0.0.1", port=8000)