import subprocess
import boto3
import argparse
import logging
import json
from subprocess import check_call

# import os

# _script_name = os.path.basename(__file__)
_script_name = "ecs-exec"
_service = "ecs"

logger = logging.getLogger()
logger.setLevel(logging.WARNING)
logging.basicConfig(
    format="[%(asctime)s] "
    + _script_name
    + " [%(levelname)s] %(funcName)s %(lineno)d: %(message)s"
)

TASK_NOT_FOUND = "The task provided in the request was " "not found."


def get_container_runtime_id(client, container_name, task_id, cluster_name):
    describe_tasks_params = {"cluster": cluster_name, "tasks": [task_id]}
    describe_tasks_response = client.describe_tasks(**describe_tasks_params)
    # need to fail here if task has failed in the intermediate time
    tasks = describe_tasks_response["tasks"]
    if not tasks:
        raise ValueError(TASK_NOT_FOUND)
    response = describe_tasks_response["tasks"][0]["containers"]
    for container in response:
        if container_name == container["name"]:
            return container["runtimeId"]


def build_ssm_request_paramaters(response, client):
    cluster_name = response["clusterArn"].split("/")[-1]
    task_id = response["taskArn"].split("/")[-1]
    container_name = response["containerName"]
    # in order to get container run-time id
    # we need to make a call to describe-tasks
    container_runtime_id = get_container_runtime_id(
        client, container_name, task_id, cluster_name
    )
    target = "ecs:{}_{}_{}".format(cluster_name, task_id, container_runtime_id)
    ssm_request_params = {"Target": target}
    return ssm_request_params


def main():
    """
    Given terraform output json formatted file that contains cluster_id and main_task_arn,
    run --command inside --container
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--command", type=str, required=True, help="Command to execute inside container"
    )

    parser.add_argument(
        "--container",
        type=str,
        required=False,  # Is required, if not supplied we print out valid container names :pray:
        help="Container in which the command should be run",
    )

    parser.add_argument(
        "--file", type=str, required=True, help="terraform output json formatted file"
    )

    args = parser.parse_args()
    session_source = boto3.Session()
    session_client = session_source.client(_service)

    # ensure session-manager-plugin is installed
    try:
        check_call(
            ["session-manager-plugin"],
            stdout=subprocess.DEVNULL,
        )
    except:
        logging.error("Please ensure session-manager-plugin is installed correctly")
        exit(1)

    with open(args.file) as file:
        terraform_output = json.load(file)

        if not type(terraform_output) is dict:
            logging.error(f"unable to parse {args.file}")
            exit(1)

        for required_key in ["cluster_id", "main_task_arn"]:
            if (
                not required_key in terraform_output
                or len(terraform_output[required_key]) == 0
            ):
                logging.error(f"could not find the {required_key}... Aborting")
                exit(1)

    cluster_name = terraform_output["cluster_id"].split("/")[-1]
    main_task_arn = terraform_output["main_task_arn"][0].split("/")[-1]
    main_task_name = main_task_arn.split(":")[0]

    try:
        taskArns = session_client.list_tasks(
            cluster=terraform_output["cluster_id"], serviceName=main_task_name
        )
    except:
        logging.error("Could not retrieve a list of tasks from cluster")
        exit(1)

    selectedTaskArn = taskArns["taskArns"][-1]  # Always use the last taskArn
    try:
        tasks = session_client.describe_tasks(
            cluster=terraform_output["cluster_id"], tasks=[selectedTaskArn]
        )
    except:
        logging.error(
            "Could not describe tasks for taskArn {} in cluster {}".format(
                selectedTaskArn, cluster_name
            )
        )
        exit(1)

    if not args.container:
        logging.error("Please supply one of the following container names:")
        for i in tasks["tasks"][0]["containers"]:
            logging.error("{}".format(i["name"]))
        exit(1)

    try:
        response = session_client.execute_command(
            cluster=cluster_name,
            container=args.container,
            command=args.command,
            interactive=True,
            task=selectedTaskArn,
        )
    except:
        logging.error("Could not execute command")
        exit(1)

    region_name = session_client.meta.region_name
    profile_name = (
        session_source.profile_name if session_source.profile_name is not None else ""
    )
    endpoint_url = session_client.meta.endpoint_url
    ssm_request_params = build_ssm_request_paramaters(response, session_client)
    """Call the session-manager-plugin with the correct inputs to initialise the remote session"""
    check_call(
        [
            "session-manager-plugin",
            json.dumps(response["session"]),
            region_name,
            "StartSession",
            profile_name,
            json.dumps(ssm_request_params),
            endpoint_url,
        ]
    )


if __name__ == "__main__":
    main()
