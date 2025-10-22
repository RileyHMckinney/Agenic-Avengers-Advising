<<<<<<< HEAD
Agenic Avengers Advising – AI Job Search Agent
An AI-powered job-search assistant built on AWS Bedrock using Anthropic Claude 3 Sonnet. This
agent interprets user messages, extracts job intent (query + location), and fetches real job listings using
the integrated JobSearchTool.
System Overview
'''
Agenic-Avengers-Advising/
│
├── agent_bedrock.py            ← Main agent file (Claude + tool integration)
├── tools/
│   ├── api_clients/
│       └── serpapi_client.py  ← Direct Communication with serp api and handles AWS secret retrieval
│   └── tool_wrappers/
│       └── job_search_tool.py  ← JobSearchTool for fetching job data
│
├── .env                        ← Environment variables (not committed)
├── requirements.txt             ← Python dependencies
└── README.md                    ← This file
'''

1. Prerequisites
- Python 3.11+ (recommended 3.12 or 3.13)
- pip package manager
- AWS CLI installed and configured
- An active AWS account with permissions for:
- bedrock:InvokeModel
- bedrock:InvokeModelWithResponseStream
- Access to the Anthropic Claude 3 Sonnet model in AWS Bedrock

2. AWS Credentials Setup
Run: aws configure
Then enter your AWS credentials and region (us-east-1).
Verify setup using: aws sts get-caller-identity

3. Environment Variables
Create a .env file with:
JOB_TOOL_MODE = "local"
SERPAPI_SECRET_NAME = "Agenic/SerpApiKey"
AWS_REGION = "us-east-1"

4. Install Dependencies
pip install -r requirements.txt
Required packages:
boto3
python-dotenv
requests

5. Model Configuration
Default model: anthropic.claude-3-sonnet-20240229-v1:0
To change it, edit MODEL_ID in agent_bedrock.py.

6. Run a Test Query
python -c "from agent_bedrock import agent_handle; print(agent_handle('find software engineer
internships in Austin'))"
Expected Output: JSON response with query, location, and job results.

7. How It Works
agent_bedrock.py:
1. Sends user message to Claude 3.
2. Model returns structured JSON.
3. Calls JobSearchTool.run() for job listings.
4. Returns the combined result.
JobSearchTool:
Fetches Google Jobs data using SerpAPI or local mode.

8. Developer Workflow
1. Create branch: git checkout -b feature/
2. Edit and test locally.
3. Commit: git add . && git commit -m "message"
4. Push: git push origin feature/

9. Run as Local API
Flask Example:
from flask import Flask, request, jsonify
from agent_bedrock import agent_handle
app = Flask(__name__)
@app.route("/agent", methods=["POST"])
def chat():
user_message = request.json.get("message", "")
result = agent_handle(user_message)
return jsonify(result)
if __name__ == "__main__":
app.run(debug=True, port=5000)

10. Troubleshooting
ValidationException → use anthropic.claude-3-sonnet-20240229-v1:0
NoCredentialsError → run aws configure
Model returned non-JSON → check DEBUG output
AccessDeniedException → ensure bedrock:InvokeModel permission

11. Example IAM Policy
{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Action": [
"bedrock:InvokeModel",
"bedrock:InvokeModelWithResponseStream"
],
"Resource": "*"
}
]
}

12. Next Steps
- Add new tools (ResumeParserTool, SalaryEstimatorTool)
- Build a frontend (React, Streamlit)
- Deploy via AWS Lambda or ECS
- Add DynamoDB/S3 memory
- Cache frequent job searches
=======
# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
>>>>>>> master
