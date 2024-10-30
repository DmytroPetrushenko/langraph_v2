from workflows.host_team import launcher_host_team
from workflows.planning_team import launch_workflow

task = 'Please investigate this host: 10.10.11.23'

task_planning_team = ("To begin the investigation of the host 10.10.11.23, I will first request a preliminary plan "
                      "from the Planner Team. This plan will outline the initial steps and methodologies to identify "
                      "potential vulnerabilities on the host. Planner Team, could you please provide a preliminary "
                      "investigation plan for the host 10.10.11.23?")

launcher_host_team(
    task=task
)


# launch_workflow(task_planning_team)

