#!/usr/bin/env python
"""
Description:
    Spawn an actionlib action server, then create a state machine that sends
    some goals to the action server that will automatically succeed or abort.
    We expect the first goal to succeed, and the second goal to abort, so
    when the second goal aborts, we map that onto success of the state
    machine.

Usage:
    $> ./actionlib.py

Output:
    [INFO] [smach_ros]: State machine starting in initial state 'GOAL_DEFAULT' with userdata:
            []
    [INFO] [smach_example_actionlib]: Executing goal...
    [INFO] [smach_ros]: State machine transitioning 'GOAL_DEFAULT':'succeeded'-->'GOAL_STATIC'
    [INFO] [smach_example_actionlib]: Executing goal...
    [INFO] [smach_ros]: State machine terminating 'GOAL_STATIC':'aborted':'succeeded'
    [INFO] [smach_example_actionlib]: Returned outcome: succeeded
"""

import rclpy
import rclpy.logging
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
import smach
import smach_ros
from smach_ros import SmachNode
from smach_tutorials.action import Test


# Create a trivial action server
class TestServer:
    def __init__(self, node: Node, name: str) -> None:
        self._sas = ActionServer(
            node=node,
            action_type=Test,
            action_name=name,
            execute_callback=self.execute_callback,
        )
        self.node = node

    def execute_callback(self, goal_handle: ServerGoalHandle) -> Test.Result:
        self.node.get_logger().info("Executing goal...")

        if goal_handle.request.goal == 0:
            goal_handle.succeed()
        elif goal_handle.request.goal == 1:
            goal_handle.abort()
        elif goal_handle.request.goal == 2:
            goal_handle.canceled()
        return Test.Result()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = SmachNode("smach_example_actionlib")
    logger = node.get_logger()
    node.start()

    # Start an action server
    TestServer(node, "test_action")

    # Create a SMACH state machine
    sm0 = smach.StateMachine(outcomes=["succeeded", "aborted", "preempted"])

    # Open the container
    with sm0:
        # Add states to the container

        # Add a simple action state. This will use an empty, default goal
        # As seen in TestServer above, an empty goal will always return with
        # GoalStatus.SUCCEEDED, causing this simple action state to return
        # the outcome 'succeeded'
        smach.StateMachine.add(
            "GOAL_DEFAULT",
            smach_ros.SimpleActionState(node, "test_action", Test),
            {"succeeded": "GOAL_STATIC"},
        )

        # Add another simple action state. This will give a goal
        # that should abort the action state when it is received, so we
        # map 'aborted' for this state onto 'succeeded' for the state machine.
        smach.StateMachine.add(
            "GOAL_STATIC",
            smach_ros.SimpleActionState(
                node, "test_action", Test, goal=Test.Goal(goal=1.0)
            ),
            {"aborted": "succeeded"},
        )

        # For more examples on how to set goals and process results, see
        # executive_python/smach/tests/smach_actionlib.py

    # Execute SMACH plan
    outcome = sm0.execute()
    logger.info(f"Returned outcome: {outcome}")


if __name__ == "__main__":
    main()
