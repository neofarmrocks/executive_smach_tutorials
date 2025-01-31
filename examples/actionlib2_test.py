#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
import rclpy.logging
from rclpy.node import Node
import smach
import smach_ros
from smach_ros import SmachNode
from action_tutorials_interfaces.action import Fibonacci


# Create a trivial action server
class TestServer:
    def __init__(self, node: Node, name: str) -> None:
        self._sas = ActionServer(
            node=node,
            action_type=Fibonacci,
            action_name=name,
            execute_callback=self.execute_callback,
        )
        self.node = node

    def execute_callback(self, goal_handle: ServerGoalHandle) -> Fibonacci.Result:
        self.node.get_logger().info("Executing goal...")

        sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            sequence.append(sequence[i] + sequence[i - 1])

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.sequence = sequence

        self.node.get_logger().info(f"{sequence}")
        return result


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
            smach_ros.SimpleActionState(node, "test_action", Fibonacci),
            {"succeeded": "GOAL_STATIC"},
        )

        # Add another simple action state. This will give a goal
        # that should abort the action state when it is received, so we
        # map 'aborted' for this state onto 'succeeded' for the state machine.
        smach.StateMachine.add(
            "GOAL_STATIC",
            smach_ros.SimpleActionState(
                node,
                "test_action",
                Fibonacci,
                goal=Fibonacci.Goal(goal=1000),
            ),
            {"aborted": "GOAL_CB"},
        )

        # Add another simple action state. This will give a goal
        # that should abort the action state when it is received, so we
        # map 'aborted' for this state onto 'succeeded' for the state machine.
        def goal_callback(
            _userdata: smach.UserData,
            default_goal: int = 10,
        ) -> Fibonacci.Goal:
            goal = Fibonacci.Goal()
            goal.order = default_goal
            return goal

        smach.StateMachine.add(
            "GOAL_CB",
            smach_ros.SimpleActionState(
                node,
                "test_action",
                Fibonacci,
                goal_cb=goal_callback,
            ),
            {"aborted": "succeeded"},
        )

        # For more examples on how to set goals and process results, see
        # executive_smach/smach_ros/tests/smach_actionlib.py
    # Execute SMACH plan
    outcome = sm0.execute()
    logger.info(f"Returned outcome: {outcome}")


if __name__ == "__main__":
    main()
