from flask import Flask, request, jsonify
import requests
import json
import zulu
import datetime
import dateutil 
import dateutil.relativedelta
from typing import List

app = Flask(__name__)

GITHUB_CONNECTION_URL = 'http://github-connection-service.github-connection:8000'
DYNAMODB_CONNECTION_URL = 'http://db-connection-service.db-connection:5000'

def obtain_github_token():
    response = requests.get(f'{GITHUB_CONNECTION_URL}/api/github/token')
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code} - {response.text}')
        return None

@app.route("/")
def index():
    return {"message": "Managing the Data Retrieval"}

@app.route("/user/contributions")
def retrive_user_contributions():
    contributor = request.args.get('contributor')
    organization = request.args.get('organization')
    repo = request.args.get('repo')

    # 4 Metrics [ COMMITS, ISSUES, PRS, STARS]
    FOR_COMMITS_URL = f"https://api.github.com/repos/{organization}/{repo}/stats/contributors"
    FOR_ISSUES_PRS_URL = f"https://api.github.com/repos/{organization}/{repo}/issues"
    FOR_REPO_STARS_URL = f"https://api.github.com/repos/{organization}/{repo}/stargazers"

    try:
        commits_weekly = {}
        commits_monthly = {}
        commits_yearly = {}
        num_issues_created_year  = 0
        num_issues_created_month = 0
        num_issues_created_week  = 0
        num_prs_created_year  = 0
        num_prs_created_month = 0
        num_prs_created_week  = 0

        valid_contributor = False

        API_TOKEN = obtain_github_token()
        print(API_TOKEN)

        response = requests.get(FOR_COMMITS_URL, headers={"Authorization": 'token %s' % API_TOKEN})
        print("status_code", response.status_code)

        if response.status_code == 200:
            stat_list = response.json()
            for stat in stat_list:
                if stat['author']["login"] == contributor:
                    commits_weekly = stat["weeks"][-1]
                    commits_monthly = commit_calculator(stat["weeks"][-4:])
                    commits_yearly = commit_calculator(stat["weeks"][-52:])
                    valid_contributor = True
                    break

            duration_year  = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(years=1))).split('.')[0]
            duration_month = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=1))).split('.')[0]
            duration_week  = str(zulu.parse(datetime.datetime.now() - dateutil.relativedelta.relativedelta(weeks=1))).split('.')[0]

            # FOR ISSUES
            issues_url_year  = f"{FOR_ISSUES_PRS_URL}?creator={contributor}&since={duration_year}"
            issues_url_month = f"{FOR_ISSUES_PRS_URL}?creator={contributor}&since={duration_month}"
            issues_url_week  = f"{FOR_ISSUES_PRS_URL}?creator={contributor}&since={duration_week}"

            response_year_issues = requests.get(issues_url_year, headers={"Authorization": 'token %s' % API_TOKEN})
            response_month_issues = requests.get(issues_url_month, headers={"Authorization": 'token %s' % API_TOKEN})
            response_week_issues = requests.get(issues_url_week, headers={"Authorization": 'token %s' % API_TOKEN})

            if response_year_issues.status_code == 200 and response_month_issues.status_code == 200 and response_week_issues.status_code == 200:
                num_issues_created_year  = len(response_year_issues.json())
                num_issues_created_month = len(response_month_issues.json())
                num_issues_created_week  = len(response_week_issues.json())

            elif response.status_code == 202:
                return "Please Try Again for Issues!"
            else:
                return f'Error for Issues: {response.status_code} - {response.text}'

            # FOR PRS
            pr_url_year  = f"{FOR_ISSUES_PRS_URL}?creator={contributor}&since={duration_year}&pulls=true&state=all"
            pr_url_month = f"{FOR_ISSUES_PRS_URL}?creator={contributor}&since={duration_month}&pulls=true&state=all"
            pr_url_week  = f"{FOR_ISSUES_PRS_URL}?creator={contributor}&since={duration_week}&pulls=true&state=all"

            response_year_prs = requests.get(pr_url_year, headers={"Authorization": 'token %s' % API_TOKEN})
            response_month_prs = requests.get(pr_url_month, headers={"Authorization": 'token %s' % API_TOKEN})
            response_week_prs = requests.get(pr_url_week, headers={"Authorization": 'token %s' % API_TOKEN})

            if response_year_prs.status_code == 200 and response_month_prs.status_code == 200 and response_week_prs.status_code == 200:
                num_prs_created_year  = len(response_year_prs.json())
                num_prs_created_month = len(response_month_prs.json())
                num_prs_created_week  = len(response_week_prs.json())

            elif response.status_code == 202:
                return "Please Try Again for PRs!"
            else:
                return f'Error for PRs: {response.status_code} - {response.text}'

            # FOR STARRED
            response_stars = requests.get(FOR_REPO_STARS_URL, headers={"Authorization": 'token %s' % API_TOKEN})
            if response_stars.status_code == 200:
                starred_count = len(response_stars.json())
            else:
                return f'Error for Starred: {response_stars.status_code} - {response_stars.text}'

            if valid_contributor:
                final_statistics = {
                    "contributor" : contributor,
                    "periodical_statistics":{
                        "week":{
                            "commit_additions"  :commits_weekly["a"],
                            "commit_deletions"  :commits_weekly["d"],
                            "number_of_commits" :commits_weekly["c"],
                            "issues_created": num_issues_created_week,
                            "prs_created": num_prs_created_week
                        },
                        "month":{
                            "commit_additions"  :commits_monthly["a"],
                            "commit_deletions"  :commits_monthly["d"],
                            "number_of_commits" :commits_monthly["c"],
                            "issues_created": num_issues_created_month,
                            "prs_created": num_prs_created_month
                        },
                        "year":{
                            "commit_additions"  :commits_yearly["a"],
                            "commit_deletions"  :commits_yearly["d"],
                            "number_of_commits" :commits_yearly["c"],
                            "issues_created": num_issues_created_year,
                            "prs_created": num_prs_created_year,
                            "starred": starred_count
                        }
                    }
                }
                print(final_statistics)
                response = requests.post(f'{DYNAMODB_CONNECTION_URL}/api/dynamodb/put_item', json=final_statistics)
                if response.status_code == 200:
                    return {'message': 'Item put into DynamoDB successfully'}
                else:
                    return f'Error: {response.status_code} - {response.text}'

                # return jsonify(final_statistics)
            else:
                return f"No contributor found with the name {contributor}!"

        else:
            return f'Error: {response.status_code} - {response.text}'

    except requests.exceptions.RequestException as exp:
        return f"Error Occurred when fetching commits: {exp}"


def commit_calculator(commit_list):
    overall_additions = 0
    overall_deletions = 0
    overall_commits   = 0

    for i in range(len(commit_list)):
        overall_additions += commit_list[i]["a"]
        overall_deletions += commit_list[i]["d"]
        overall_commits   += commit_list[i]["c"]

    calculated_commit_stats = {
        "a": overall_additions,
        "d": overall_deletions,
        "c": overall_commits
    }

    return calculated_commit_stats

@app.route('/contributors')
def retrive_all_contributors():
    organization = request.args.get('organization')
    repo = request.args.get('repo')

    API_TOKEN = obtain_github_token()
    print('API TOKEN', API_TOKEN)
    print(organization)
    print(repo)

    URL = f"https://api.github.com/repos/{organization}/{repo}/stats/contributors"
    response = requests.get(URL, headers={"Authorization": 'token %s' % API_TOKEN})

    if response.status_code == 200:
        return jsonify(response.json())
    elif response.status_code == 202:
        return "Please Try Again!"
    else:
        return f'Error: {response.status_code} - {response.text}'

@app.route('/user/performance')
def get_user_performance():
    contributor = request.args.get('contributor')
    print(contributor)

    response = requests.get(f'{DYNAMODB_CONNECTION_URL}/api/dynamodb/get_item', params={'contributor': contributor})

    # Check the response status code
    if response.status_code == 200:
        # Successfully received data from the service
        # result = response.json()
        performance_data = calculate_performance(response.json())
        print(performance_data)
        metrics_data = {
            "week_performance": calculate_metrics(performance_data["week_performance"]),
            "month_performance": calculate_metrics(performance_data["month_performance"]),
            "year_performance": calculate_metrics(performance_data["year_performance"])
        }

        print(metrics_data)
        return metrics_data
        print(result)
    elif response.status_code == 404:
        # Item not found
        return "Item not found"
    else:
        # Other error occurred
        return f'Error: {response.status_code} - {response.text}'

def calculate_performance(data):
    week_performance = {
        "commit_additions": int(data.get("WeekCommitAdditions", 0)),
        "commit_deletions": int(data.get("WeekCommitDeletions", 0)),
        "number_of_commits": int(data.get("WeekNumberOfCommits", 0)),
        "issues_created": int(data.get("WeekIssuesCreated", 0)),
        "prs_created": int(data.get("WeekPRsCreated", 0)),
        "starred": int(data.get("Starred", 0))
    }

    month_performance = {
        "commit_additions": int(data.get("MonthCommitAdditions", 0)),
        "commit_deletions": int(data.get("MonthCommitDeletions", 0)),
        "number_of_commits": int(data.get("MonthNumberOfCommits", 0)),
        "issues_created": int(data.get("MonthIssuesCreated", 0)),
        "prs_created": int(data.get("MonthPRsCreated", 0)),
        "starred": int(data.get("Starred", 0))
    }

    year_performance = {
        "commit_additions": int(data.get("YearCommitAdditions", 0)),
        "commit_deletions": int(data.get("YearCommitDeletions", 0)),
        "number_of_commits": int(data.get("YearNumberOfCommits", 0)),
        "issues_created": int(data.get("YearIssuesCreated", 0)),
        "prs_created": int(data.get("YearPRsCreated", 0)),
        "starred": int(data.get("Starred", 0))
    }

    return {
        "week_performance": week_performance,
        "month_performance": month_performance,
        "year_performance": year_performance,
    }

def calculate_metrics(data):
    commit_activity_metrics = {
        "total_commit_additions": data["commit_additions"],
        "total_commit_deletions": data["commit_deletions"],
        "total_commits": data["commit_additions"] + data["commit_deletions"],
        "net_commits": data["commit_additions"] - data["commit_deletions"],
        "commit_ratio": (data["commit_additions"] / max(data["commit_deletions"], 1)),
    }

    issue_pr_metrics = {
        "total_issues": data["issues_created"] ,
        "total_prs": data["prs_created"] ,
        "issue_pr_ratio": (data["issues_created"] / max(data["prs_created"] , 1)),
    }

    general_metrics = {
        "commit_impact": (
            2 * data["commit_additions"] - data["commit_deletions"] + 1.5 * data["number_of_commits"] 
        ),
        "starred": data["starred"]
    }

    return {
        "commit_activity_metrics": commit_activity_metrics,
        "issue_pr_metrics": issue_pr_metrics,
        "general_metrics": general_metrics,
        "overall_performance_score": (
            0.4 * commit_activity_metrics["net_commits"]
            + 0.3 * issue_pr_metrics["issue_pr_ratio"]
            + 0.3 * general_metrics["commit_impact"]
        ) 
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)