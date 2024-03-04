# DeveloperIQ_Solution

DeveloperIQ is a developer productivity tracker. Its main purpose is to track how productive a developer is.

## Overview

In the dynamic landscape of software development, the requirement to optimize and calculate developer productivity is a foremost factor and in order to achieve this in this, a carefully considered microservices architecture operates within a Kubernetes cluster is used.

Through the GitHub REST API, mainly 4 metrics were selected to address this issue:

  1.	Commit activity per developer
      •	Commit additions
      •	Commit deletions
      •	Number of total commits
  2.	Issues assigned for a user
  3.	Pull Requests for a user
  4.	Number of stars for a repo owned by a user

In order to create an application that can calculate developer productivity, connect to GitHub API and then record the values in a database, 3 microservices were implemented using Python language, and was stored under 3 separate repositories to achieve high-level of independence considering deployable and scalable factors. Thus, development and deployment processes can be managed and optimized for each microservice separately without affecting others.

### NOTE: This repository contains all the services together for better understanding but to be able to run the CI/CD pipelines and work as microservices, the 3 folders in this repository should be inserted to 3 repositories seperately as shown below.

![alt text](https://github.com/dinisurunisal/DeveloperIQ_Solution/edit/main/images/repository_structure.jpg?raw=true)
