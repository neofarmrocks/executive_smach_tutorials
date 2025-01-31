#!/usr/bin/env python3
"""
Description:

Usage:
    $> ./user_data2.py

Output:
    [INFO] [smach_ros]: State machine starting in initial state 'FOO' with userdata:
            ['sm_counter']
    [INFO] [smach_example_state_machine]: Executing state FOO
    [INFO] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [smach_example_state_machine]: Executing state BAR
    [INFO] [smach_example_state_machine]: Counter = 1
    [INFO] [smach_ros]: State machine transitioning 'BAR':'outcome1'-->'FOO'
    [INFO] [smach_example_state_machine]: Executing state FOO
    [INFO] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [smach_example_state_machine]: Executing state BAR
    [INFO] [smach_example_state_machine]: Counter = 2
    [INFO] [smach_ros]: State machine transitioning 'BAR':'outcome1'-->'FOO'
    [INFO] [smach_example_state_machine]: Executing state FOO
    [INFO] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [smach_example_state_machine]: Executing state BAR
    [INFO] [smach_example_state_machine]: Counter = 3
    [INFO] [smach_ros]: State machine transitioning 'BAR':'outcome1'-->'FOO'
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
        RosState.__init__(
            self,
            node,
            outcomes=["outcome1", "outcome2"],
            input_keys=["foo_counter_in"],
            output_keys=["foo_counter_out"],
        )
        self.logger = node.get_logger()

    def execute(self, userdata: smach.UserData) -> str:
        self.logger.info("Executing state FOO")
        if userdata.foo_counter_in < 3:
            userdata.foo_counter_out = userdata.foo_counter_in + 1
            return "outcome1"
        return "outcome2"


# define state Bar
class Bar(RosState):
    def __init__(self, node: Node) -> None:
        RosState.__init__(
            self, node, outcomes=["outcome1"], input_keys=["bar_counter_in"]
        )
        self.logger = node.get_logger()

    def execute(self, userdata: smach.UserData) -> str:
        self.logger.info("Executing state BAR")
        self.logger.info(f"Counter = {userdata.bar_counter_in}")
        return "outcome1"


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = SmachNode("smach_example_state_machine")
    logger = node.get_logger()
    node.start()

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=["outcome4"])
    sm.userdata.sm_counter = 0

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add(
            "FOO",
            Foo(node),
            transitions={"outcome1": "BAR", "outcome2": "outcome4"},
            remapping={"foo_counter_in": "sm_counter", "foo_counter_out": "sm_counter"},
        )
        smach.StateMachine.add(
            "BAR",
            Bar(node),
            transitions={"outcome1": "FOO"},
            remapping={"bar_counter_in": "sm_counter"},
        )

    # Execute SMACH plan
    outcome = sm.execute()
    logger.info(f"Returned outcome: {outcome}")


if __name__ == "__main__":
    main()
