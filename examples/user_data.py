#!/usr/bin/env python3
"""
Description:
    Create a two-state state machine where one state writes to userdata and
    the other state reads from userdata, and spews a message to rosout.

Usage:
    $> ./user_data.py

Output:
    [  INFO ] : State machine starting in initial state 'SET' with userdata:
            []
    [  INFO ] : State machine transitioning 'SET':'set_it'-->'GET'
    [INFO] [smach_example_state_machine_nesting]: >>> GOT DATA! x = True
    [  INFO ] : State machine terminating 'GET':'got_it':'succeeded'
    [INFO] [smach_example_state_machine_nesting]: Returned outcome: succeeded
"""

import rclpy
import rclpy.logging
from rclpy.node import Node
import smach


class Setter(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=["set_it"], output_keys=["x"])

    def execute(self, ud):
        ud.x = True
        return "set_it"


class Getter(smach.State):
    def __init__(self, node: Node):
        smach.State.__init__(self, outcomes=["got_it"], input_keys=["x"])
        self.logger = node.get_logger()

    def execute(self, ud):
        self.logger.info(">>> GOT DATA! x = " + str(ud.x))
        return "got_it"


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = Node("smach_example_state_machine_nesting")
    logger = node.get_logger()

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=["succeeded"])

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add("SET", Setter(), {"set_it": "GET"})
        smach.StateMachine.add("GET", Getter(node), {"got_it": "succeeded"})

    # Execute SMACH plan
    outcome = sm.execute()
    logger.info(f"Returned outcome: {outcome}")


if __name__ == "__main__":
    main()
