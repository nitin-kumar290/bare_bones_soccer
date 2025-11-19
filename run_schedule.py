# fire_schedule.py
import boto3

sched = boto3.client("scheduler", region_name="us-east-2")
resp = sched.start_schedule(
    Name="barebones-weekly-reminder-email",
    ScheduleGroupName="default"
)
print("Response:", resp)