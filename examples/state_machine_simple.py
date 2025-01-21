#!/usr/bin/env python
"""
Description:

Usage:
    $> ./state_machine_simple.py

Output:
    [INFO] [smach_ros]: State machine starting in initial state 'FOO' with userdata:
            []
    [INFO] [smach_example_state_machine]: Executing state FOO
    [INFO] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [smach_example_state_machine]: Executing state BAR
    [INFO] [smach_ros]: State machine transitioning 'BAR':'outcome2'-->'FOO'
    [INFO] [smach_example_state_machine]: Executing state FOO
    [INFO] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [smach_example_state_machine]: Executing state BAR
    [INFO] [smach_ros]: State machine transitioning 'BAR':'outcome2'-->'FOO'
    [INFO] [smach_example_state_machine]: Executing state FOO
    [INFO] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [smach_example_state_machine]: Executing state BAR
    [INFO] [smach_ros]: State machine transitioning 'BAR':'outcome2'-->'FOO'
    [INFO] [smach_example_state_machine]: Executing state FOO
    [INFO] [smach_ros]: State machine terminating 'FOO':'outcome2':'outcome4'
    [INFO] [smach_example_state_machine]: Returned outcome: outcome4
"""

import rclpy
import rclpy.logging
from rclpy.node import Node
import smach
from smach_ros import RosState, SmachNode


# define state Foo
class Foo(RosState):
    def __init__(self, node: Node) -> None:
        RosState.__init__(self, node, outcomes=["outcome1", "outcome2"])
        self.logger = node.get_logger()
        self.counter = 0

    def execute(self, userdata: smach.UserData) -> str:
        self.logger.info("Executing state FOO")
        if self.counter < 3:
            self.counter += 1
            return "outcome1"
        return "outcome2"


# define state Bar
class Bar(RosState):
    def __init__(self, node: Node) -> None:
        RosState.__init__(self, node, outcomes=["outcome2"])
        self.logger = node.get_logger()

    def execute(self, _userdata: smach.UserData) -> str:
        self.logger.info("Executing state BAR")
        return "outcome2"


# main
def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = SmachNode("smach_example_state_machine")
    logger = node.get_logger()
    node.start()

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=["outcome4", "outcome5"])

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add(
            "FOO",
            Foo(node),
            transitions={"outcome1": "BAR", "outcome2": "outcome4"},
        )
        smach.StateMachine.add("BAR", Bar(node), transitions={"outcome2": "FOO"})

    # Execute SMACH plan
    outcome = sm.execute()
    logger.info(f"Returned outcome: {outcome}")


if __name__ == "__main__":
    main()
