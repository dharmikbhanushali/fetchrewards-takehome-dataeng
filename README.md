# Data Engineering Take Home: ETL off a SQS Queue

## Overview

This project is a small application that reads JSON data containing user login behavior from an AWS SQS Queue, masks personal identifiable information (PII), and writes the data to a Postgres database. The application is built using Python and Docker, and uses LocalStack for local AWS services.

## Objectives

1. Read JSON data containing user login behavior from an AWS SQS Queue, that is made available via a custom LocalStack image that has the data pre-loaded.
2. Fetch wants to hide personal identifiable information (PII). The fields `device_id` and `ip` should be masked, but in a way where it is easy for data analysts to identify duplicate values in those fields.
3. Once you have flattened the JSON data object and masked those two fields, write each record to a Postgres database that is made available via a custom Postgres image that has the tables pre-created.

## Prerequisites

Ensure you have the following installed on your local machine:

- Docker
- Docker Compose
- Python 3.9.12
- `awscli-local` package (for LocalStack)
- `psql` (PostgreSQL command line tool)

## Setup Instructions

1. **Clone the Repository:**
   ```sh
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Start your Docker daemon:**
   Ensure Docker is running on your machine.

3. **Check if the containers are running and images are created:**
   ```sh
   docker-compose up
   ```
   Wait for the services to start.

4. **Run the Python script:**
   ```sh
   python app.py
   ```

## Thought Process, Struggles, Decision Making, Learnings, and Step-by-Step Guide to Run the Application

I began this project with a clear goal: to read, mask, and store user login data from an SQS queue into a Postgres database. The journey was full of challenges, but it was a rewarding experience that sharpened my debugging, research, and persistence skills.

### Setting Up the Prerequisites

I started by setting up Docker Desktop, installing AWS CLI, AWS CLI Local, and initially used Python 3.10. I also installed PostgreSQL and configured it using either pgAdmin or psql CLI to monitor the database.

### Creating Dockerfiles

I created the Dockerfile to get the Postgres and LocalStack services up and running. Initially, I had just one Dockerfile for the main script, Postgres, and LocalStack images, alongside a docker-compose file to orchestrate and run everything. However, I soon encountered an architecture error: "linux/arm64 does not work on your system architecture." I resolved this by setting it to "linux/amd64."

### Debugging Docker Issues

Building the Docker images was successful, and the container was up and running. But the script couldn't fetch the queue due to endpoint URL issues, indicating problems with overlapping dependencies and libraries. I used the command `curl http://localhost:4566/health` to check if LocalStack services were running, but they weren't. I spent some time debugging but eventually got lost in a web of errors.

### Adapting to Python 3.9.12

I decided to start fresh with Python 3.9.12 as I learned from the research that boto libraries do not work with python 3.10 or higher versions. I separated the components into individual Dockerfiles for Postgres, LocalStack, and the main script. Using `docker buildx` commands, I built Dockerfiles specific to the system architecture. I encountered a warning: "No output specified with docker-container driver. Build result will only remain in the build cache." I resolved this by using the `--load` command to load images into the containers for local use, and the services started running.

### Ensuring Services are Running

Using `curl http://localhost:4566/health` again, I verified that the services were up. The response confirmed that SQS was running. I also used `docker exec -it fetchrewards-take2-dataeng-postgres-1 psql -U postgres` to check the database connection, which was successful.

### Addressing Library Compatibility Issues

The script still didn't fetch data from the SQS queue due to library issues. The error `ImportError: cannot import name 'is_s3express_bucket' from 'botocore.utils'` was caused by incompatible versions of boto3, botocore, and s3transfer. Through extensive research and reading GitHub threads, I learned that the latest versions were unstable. Manually installing specific versions resolved this issue:

```plaintext
boto3==1.33.2
botocore==1.33.2
s3transfer==0.8.1
psycopg2-binary
```

### Resolving Credential Errors

Next, I faced `botocore.exceptions.NoCredentialsError: Unable to locate credentials`. Although an AWS account wasn't needed, specifying dummy AWS config and credentials in the script was necessary. After referencing various Stack Overflow discussions and official documentation, I included dummy AWS credentials in the script.

### Final Adjustments

While running the script, I encountered a minor import error due to using different Python environments. Switching to Python 3.9.12 and ensuring consistent library usage resolved this. The final hurdle was a faulty database schema while inserting data. After correcting the schema, the data was fetched and inserted correctly. Debugging with `pprint` confirmed that the data was received correctly from the JSON body.

### Verifying Data Insertion

To verify data insertion into the Postgres database (`user_logins` table), I used:

```sh
docker exec -it fetchrewards-take2-dataeng-postgres-1 psql -U postgres
```
Within the psql CLI, running a select query confirmed that the data was correctly written. Alternatively, pgAdmin can be used for a graphical interface.

### Conclusion

Throughout this journey, I demonstrated resilience, problem-solving, and a passion for learning. Each challenge was an opportunity to refine my skills, from debugging and research to adapting quickly to new solutions. This project was not just about achieving the objectives but also about embracing the learning process and enjoying the problem-solving adventure.

## Decision-Making

### How will you read messages from the queue?
We use the `boto3` library to read messages from the AWS SQS queue because it integrates well with AWS and is easy to use in Python. The application pulls messages in batches of up to 10 at a time, which makes the process more efficient.

### What type of data structures should be used?
We use dictionaries, a core Python data structure, to handle the JSON data from the queue messages. This makes it easy to manipulate the data and prepare it for database insertion.

### How will you mask the PII data so that duplicate values can be identified?
We mask PII data like `device_id` and `ip` addresses using the SHA-256 hashing function from Python's `hashlib` module. SHA-256 is consistent, meaning the same input always gives the same output, which is essential for spotting duplicates in the masked data.

### What will be your strategy for connecting and writing to Postgres?
We connect to the PostgreSQL database using the `psycopg2` library, which is well-supported and widely used for working with PostgreSQL in Python. It allows us to run SQL commands safely and efficiently.

### Where and how will your application run?
The application runs inside Docker containers. Docker helps package the application with all its dependencies, ensuring it works the same way in any environment. Docker Compose manages these containers, including our services like LocalStack for AWS simulation and PostgreSQL.

## Library and Technology Choices

We chose `boto3` because it's specifically made for AWS and works seamlessly with its services, making tasks like interacting with SQS straightforward. `psycopg2` is our choice for database operations due to its reliability and comprehensive feature set, which are great for handling data securely and efficiently in Python.

We use SHA-256 for hashing because it's secure and fast, making it ideal for our needs. It ensures that even large data volumes are processed quickly and safely.

These choices help make sure our application is secure, efficient, and easy to maintain, regardless of where it's deployed.

---

## Next Steps

### How would you deploy this application in production?

For production deployment, I'd move the application from LocalStack to actual AWS services. I would use AWS CloudFormation or Terraform for infrastructure as code, allowing automated and repeatable setups. Additionally, setting up proper CI/CD pipelines using tools like Jenkins or GitHub Actions would ensure smooth deployment and updates.

### What other components would you want to add to make this production ready?

To make this application production-ready, I would implement logging and monitoring using AWS CloudWatch to track the application’s performance and errors in real-time. Also, integrating proper error handling and retry mechanisms. Lastly, security measures like IAM roles and policies would be managed to secure access to AWS resources.

### How can this application scale with a growing dataset?

To scale with a growing dataset, the application could use AWS SQS message batching to increase throughput and reduce the number of API calls. For the database, leveraging PostgreSQL’s partitioning features or scaling horizontally with Amazon RDS read replicas would handle increased load. Using auto-scaling groups for the Docker containers would also help manage fluctuations in demand.

### How can PII be recovered later on?

Recovering PII once it's hashed would typically not be possible as SHA-256 is a one-way function. If recovery of original PII data is necessary, a secure encryption method should be used instead of hashing, where keys are managed with some kind of AWS service or any other services provided.

### What are the assumptions you made?

I assumed that the input data format is consistent and reliable. I also presumed that network connectivity issues are minimal to none, which may not be the case in a varied network environment. Lastly, I assumed the data volume would be manageable within the limits of a single database instance without immediate need for scaling solutions.

---

## Outputs and Images

Here are the outputs showing the new data with `masked_ip` and `masked_device_id`. Below are also images from PgAdmin confirming that the fields were masked correctly:

[User Logins CSV] - (https://github.com/dharmikbhanushali/fetchrewards-takehome-dataeng/blob/main/user_logins.csv)
[User Logins JSON] - (https://github.com/dharmikbhanushali/fetchrewards-takehome-dataeng/blob/main/user_logins.json)
![PgAdmin Screenshot](https://github.com/dharmikbhanushali/fetchrewards-takehome-dataeng/blob/main/pgadmin.png)
![Terminal pgadmin Screenshot](https://github.com/dharmikbhanushali/fetchrewards-takehome-dataeng/blob/main/terminal_output.png)
