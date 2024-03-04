from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import NotFound
from boto3.dynamodb.conditions import Key
import boto3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/")
def index():
    return jsonify({"message": "Establishing the DB Connection"})

class DynamoDBConnectionService:
    def __init__(self, table_name='developer_metrics'):
        self.table_name = table_name
        self.PRIMARY_KEY_COLUMN_NAME = "contributor"
        self.columns = ["periodical_statistics"]
        self.dynamodb = self._init_dynamodb()
        self.table = self._init_table()

    def _init_dynamodb(self):
        return boto3.resource('dynamodb', region_name='us-east-2')

    def _init_table(self):
        return self.dynamodb.Table(self.table_name)

    def put_item(self, contributor, periodical_statistics):

        # Extract values from the periodical_statistics dictionary
        week_stats = periodical_statistics.get("week", {})
        month_stats = periodical_statistics.get("month", {})
        year_stats = periodical_statistics.get("year", {})

        response = self.table.put_item( 
            Item={
                self.PRIMARY_KEY_COLUMN_NAME: contributor,
                'WeekCommitAdditions': week_stats.get("commit_additions", 0),
                'WeekCommitDeletions': week_stats.get("commit_deletions", 0),
                'WeekNumberOfCommits': week_stats.get("number_of_commits", 0),
                'WeekIssuesCreated': week_stats.get("issues_created", 0),
                'WeekPRsCreated': week_stats.get("prs_created", 0),
                'MonthCommitAdditions': month_stats.get("commit_additions", 0),
                'MonthCommitDeletions': month_stats.get("commit_deletions", 0),
                'MonthNumberOfCommits': month_stats.get("number_of_commits", 0),
                'MonthIssuesCreated': month_stats.get("issues_created", 0),
                'MonthPRsCreated': month_stats.get("prs_created", 0),
                'YearCommitAdditions': year_stats.get("commit_additions", 0),
                'YearCommitDeletions': year_stats.get("commit_deletions", 0),
                'YearNumberOfCommits': year_stats.get("number_of_commits", 0),
                'YearIssuesCreated': year_stats.get("issues_created", 0),
                'YearPRsCreated': year_stats.get("prs_created", 0),
                'Starred': year_stats.get("starred", 0)
            }
        )
        return response

    def get_item(self, contributor):
        response = self.table.get_item(Key={self.PRIMARY_KEY_COLUMN_NAME: contributor})
        return response.get('Item', None)

# Initialize DynamoDB Connection Service
dynamodb_connection_service = DynamoDBConnectionService()

@app.route('/api/dynamodb/put_item', methods=['POST'])
def put_item():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'message': 'Data not received!'})

        print(data)

        contributor = data.get('contributor')
        periodical_statistics = data.get('periodical_statistics')

        dynamodb_connection_service.put_item(contributor, periodical_statistics)
        return jsonify({'message': 'Item put into DynamoDB successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dynamodb/get_item', methods=['GET'])
def get_item():

    contributor = request.args.get('contributor')
    print(contributor)

    try:
        result = dynamodb_connection_service.get_item(contributor)
        if result:

            response = {
                "Contributor": result.get("Contributor", ""),
                "WeekCommitAdditions": result.get("WeekCommitAdditions", 0),
                "WeekCommitDeletions": result.get("WeekCommitDeletions", 0),
                "WeekNumberOfCommits": result.get("WeekNumberOfCommits", 0),
                "WeekIssuesCreated": result.get("WeekIssuesCreated", 0),
                "WeekPRsCreated": result.get("WeekPRsCreated", 0),
                "MonthCommitAdditions": result.get("MonthCommitAdditions", 0),
                "MonthCommitDeletions": result.get("MonthCommitDeletions", 0),
                "MonthNumberOfCommits": result.get("MonthNumberOfCommits", 0),
                "MonthIssuesCreated": result.get("MonthIssuesCreated", 0),
                "MonthPRsCreated": result.get("MonthPRsCreated", 0),
                "YearCommitAdditions": result.get("YearCommitAdditions", 0),
                "YearCommitDeletions": result.get("YearCommitDeletions", 0),
                "YearNumberOfCommits": result.get("YearNumberOfCommits", 0),
                "YearIssuesCreated": result.get("YearIssuesCreated", 0),
                "YearPRsCreated": result.get("YearPRsCreated", 0),
                "Starred": result.get("Starred", 0)
            }

            return jsonify(response)
        else:
            raise NotFound(description='Item not found')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
