# ecs-exec
pip installable bin to allow user to exec commands inside containers running on [AWS ECS Fargate](https://aws.amazon.com/fargate/) that relies on [terraformed](https://www.terraform.io/) infrastructure.

# Motivation
- Run commands inside containers defined by terraform on AWS ECS Fargate.

# Installation
```bash
$ pip install ecs-exec
```

# Usage
At minimum a terraform module which will output the following:
```terraform
output "cluster_id" {
  value = "${var.cluster_id}"
}

output "main_task_arn" {
  value = "${var.main_task_arn}"
}
```
`cluster_id` is used to identify the ECS cluster, and `main_task_arn` is used to identify the main task in the ECS cluster. This also assumes that you have configured the following to allow ECS exec:
- ECS cluster
- ECS task
- AWS user

Once you have applied the terraform configuration, pull the output into json:
```bash
$ terraform output -json custom_ecs_service > custom_ecs_service.json
```
Now you can run your command inside a specific container
```bash
AWS_PROFILE=staging ecs-exec --file custom_ecs_service.json --container php-fpm --command bash
```
If you do not know the container name upfront then not supplying the container will print out valid container names.

# Output
Output will look something like:
```bash
AWS_PROFILE=staging ecs-exec --file custom_ecs_service.json --container php-fpm --command "date +%F"

The Session Manager plugin was installed successfully. Use the AWS CLI to start a session.


Starting session with SessionId: ecs-execute-command-qNq9bIy0uTrZlriS
This session is encrypted using AWS KMS.
2021-06-25


Exiting session with sessionId: ecs-execute-command-qNq9bIy0uTrZlriS.
```