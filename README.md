# DeveloperIQ_Solution

DeveloperIQ is a developer productivity tracker. Its main purpose is to track how productive a developer is.

## Overview

In the dynamic landscape of software development, the requirement to optimize and calculate developer productivity is a foremost factor and in order to achieve this in this, a carefully considered microservices architecture operates within a Kubernetes cluster is used.

Through the GitHub REST API, mainly 4 metrics were selected to address this issue:

  1.	Commit activity per developer (Commit additions, Commit deletions, Number of total commits)
  2.	Issues assigned for a user
  3.	Pull Requests for a user
  4.	Number of stars for a repo owned by a user

In order to create an application that can calculate developer productivity, connect to GitHub API and then record the values in a database, 3 microservices were implemented using Python language, and was stored under 3 separate repositories to achieve high-level of independence considering deployable and scalable factors. Thus, development and deployment processes can be managed and optimized for each microservice separately without affecting others.

### NOTE: This repository contains all the services together for better understanding but to be able to run the CI/CD pipelines and work as microservices, the 3 folders in this repository should be inserted to 3 repositories seperately as shown below.

![alt text](https://github.com/dinisurunisal/DeveloperIQ_Solution/blob/main/images/repository_structure.png?raw=true)

The purpose of these microservices will be discussed under the Solution Architecture Diagram.


## Solution Architecture Diagram 

![alt text](https://github.com/dinisurunisal/DeveloperIQ_Solution/blob/main/images/solution_architecture_dig.png?raw=true)

In this implementation, AWS cloud is leveraged as the cloud platform, utilizing Amazon EKS (Elastic Kubernetes Service) for the cluster orchestration. Load Balancers were used to ensure efficient traffic distribution for the 3 services separately, while DynamoDB serves as the selected database for this architecture. For the purpose of managing and storing docker images, Amazon ECR (Elastic Container Registry) was used as the container registry and basically all the cloud services are based on AWS.

The purposes of the three services are;

#### 	Github_Connection_Service:

This service is used to get the GitHub token which is required when accessing the GitHub APIs. The token is stored in Amazon Secrets Manager as a secret because a token is a sensitive data and this ensures the security as all secrets are encrypted and only authorized individuals can access it.

#### 	Db_Connection_Service:

This service is the only service that deals with the database, in which in this case is AWS DynamoDb. When developer statistics are collected from the APIs, this service endpoint to insert data to the database is called and also when information related to a particular developer should be gathered, the endpoint to retrieve the data from the database is called.

#### 	Data_Retrieval_Service:

This service is responsible for authenticating the GitHub, retrieving developer data according to the requirement which comes under a certain repository/ organization and also sending the data to the database. All these are done by API calls to the other 2 services and this service acts like the mediator.


## Deployment Architecture Diagram 

![alt text](https://github.com/dinisurunisal/DeveloperIQ_Solution/blob/main/images/deployment_architecture_dig.png?raw=true)

The deployment architecture for this application is designed for efficiency and simplicity. Flask API is used with python in implementing the core functionality, and upon pushing the code to GitHub repo, CI/CD pipeline triggers with the use of GitHub actions. Later the Docker image is safely stored in Amazon ECR and Amazon EKS is responsible in orchestrating containers after fetching the Docker image from ECR. The continuous deployment (CD) phase ensures a seamless rollout of new versions in the production environment.
