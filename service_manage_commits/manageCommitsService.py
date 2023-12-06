from fastapi import FastAPI
import uvicorn
import boto3
import requests
from typing import List

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
    return {"message": "Managing the Commits"}

@app.get("/commits")
async def retrive_user_commits(contributer:str, organization:str, repo: str):
  URL = f"https://api.github.com/repos/{organization}/{repo}/stats/contributors"

  try:
    commits_weekly = {}
    commits_monthly = {}
    commits_yeary = {}
    valid_contributer = False

    response = requests.get(URL, headers={"Authorization": 'token %s' % api_token})
    print("status_code", response.status_code)

    if response.status_code == 200:
      stat_list = response.json()
      for stat in stat_list:
        if stat['author']["login"] == contributer:
          commits_weekly = stat["weeks"][-1]
          commits_monthly = commit_calculator(stat["weeks"][-4:])
          commits_yearly = commit_calculator(stat["weeks"][-52:])
          valid_contributer = True
          break

      if valid_contributer == True:

        final_statistics = {
          "contributor" : contributer,
          "periodical_statistics":{
            "week":{
                "commit_additions"  :commits_weekly["a"],
                "commit_deletions"  :commits_weekly["d"],
                "number_of_commits" :commits_weekly["c"]
            },
            "month":{
                "commit_additions"  :commits_monthly["a"],
                "commit_deletions"  :commits_monthly["d"],
                "number_of_commits" :commits_monthly["c"]
            },
            "year":{
                "commit_additions"  :commits_yearly["a"],
                "commit_deletions"  :commits_yearly["d"],
                "number_of_commits" :commits_yearly["c"]
            }
          }
        }
        return final_statistics
      else:
        return("No contributer found with the name {contributer}!".format(contributer=contributer))

    elif response.status_code == 202:
      return "Please Try Again!"
    else:
      return "Request Failed!"
  except requests.exceptions.RequestException as exp:
      return f"Error Occured when fetching commits: {exp}"

def commit_calculator(commit_list:List):
    overall_additions = 0
    overall_deletions = 0
    overall_commits   = 0

    for i in range(len(commit_list) + 1):

      if i > 0:
          overall_additions += commit_list[i-1]["a"]
          overall_deletions += commit_list[i-1]["d"]
          overall_commits   += commit_list[i-1]["c"]

    calculated_commit_stats = {
      "a":overall_additions,
      "d":overall_deletions,
      "c":overall_commits
    }

    return calculated_commit_stats

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