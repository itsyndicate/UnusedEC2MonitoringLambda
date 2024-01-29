# AWS Lambda EC2 Unused Instances Alert

This AWS Lambda function is designed to identify instances with low CPU utilization and low network I/O over a specified period. When instances meet the defined criteria, an alert is sent to an Amazon SNS topic.

## Inspired by AWS Trusted Advisor Monitoring

This solution takes inspiration from AWS Trusted Advisor monitoring, integrating it into a custom script. It checks the Amazon Elastic Compute Cloud (Amazon EC2) instances that were running at any time during the last 14 days. The alert triggers if the daily CPU utilization was 10% or less and network I/O was 5 MB or less on 4 or more days.

## Requirements

- Python 3.7 or later
- AWS Lambda execution role with permissions to access CloudWatch, EC2, and SNS

## Configuration

Adjust the following variables in the `lambda_handler.py` file to meet your requirements:

- `SNS_TOPIC_ARN`: ARN of the Amazon SNS topic to receive alerts.
- `threshold_days`: Number of days to consider for low utilization.
- `max_cpu_utilization`: Maximum allowed CPU utilization percentage.
- `max_network_io`: Maximum allowed network I/O in bytes.

## Usage

This Lambda function runs automatically based on the configured CloudWatch Events rule. You can monitor the Lambda function logs in the AWS CloudWatch console.

## Alerts

If instances meet the specified criteria, an alert message is sent to the configured SNS topic. If no instances match the conditions, a notification about no instances found is sent.
