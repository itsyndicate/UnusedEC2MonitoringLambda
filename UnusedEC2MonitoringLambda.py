import boto3
from datetime import datetime, timedelta
import os

def lambda_handler(event, context):
    SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
    cloudwatch = boto3.client('cloudwatch')
    sns = boto3.client('sns')
    threshold_days = 4
    max_cpu_utilization = 10.0
    max_network_io = 5 * 1024 * 1024  # 5 MB in bytes
    
    # Get the current time and time 14 days ago
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=14)
    
    # Get list of instances
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()
    
    messages = []  # List to store messages
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_name = None
            
            # Get server name (tag 'Name') if specified
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
            
            # Get CPU utilization metric data
            cpu_metric = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    },
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # Daily granularity
                Statistics=['Average']
            )
            
            # Get network I/O metric data
            network_metric = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkOut',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    },
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # Daily granularity
                Statistics=['Sum']
            )
            
            # Check if CPU and network I/O meet the conditions
            if len(cpu_metric['Datapoints']) >= threshold_days and \
               all(point['Average'] <= max_cpu_utilization for point in cpu_metric['Datapoints']) and \
               all(point['Sum'] <= max_network_io for point in network_metric['Datapoints']):
                # Form a message with the server name
                if instance_name:
                    message = f"Server {instance_name} (Instance ID: {instance_id}) had CPU utilization <= {max_cpu_utilization}% and network I/O <= 5 MB for {threshold_days} or more days."
                else:
                    message = f"Instance {instance_id} had CPU utilization <= {max_cpu_utilization}% and network I/O <= 5 MB for {threshold_days} or more days."
                messages.append(message)  # Add message to the list
    
    # Message sent if no instances meet the conditions
    if not messages:
        no_instances_message = "No instances found that meet the criteria."
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=no_instances_message,
            Subject=f'EC2 Alert about unused instances for {context.invoked_function_arn.split(":")[3]} region'
        )
        print(no_instances_message)
    else:
        # Send one message with all matches
        final_message = '\n'.join(messages)  # Concatenate all messages into one string
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=final_message,
            Subject=f'EC2 Alert about unused instances for {context.invoked_function_arn.split(":")[3]} region'
        )
        print(final_message)

