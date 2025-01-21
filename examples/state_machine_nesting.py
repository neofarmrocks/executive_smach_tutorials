#!/usr/bin/env python
"""
Description:
    Create one state machine, put a state in it that sets something in the
    userdata key 'x'. Put another state machine inside of that state machine,
    tell it to fetch the userdata key 'x'. Put a state that reads 'x' into
    that nested state machine, and spew some info to rosout.

Usage:
    $> ./state_machine_nesting.py

Output:
    [  INFO ] : State machine starting in initial state 'SET' with userdata:
            []
    [INFO]  [smach_example_state_machine_nesting]: >>> Set data: hello
    [  INFO ] : State machine transitioning 'SET':'set_it'-->'NESTED'
    [  INFO ] : State machine starting in initial state 'GET' with userdata:
            ['x']
    [INFO] [smach_example_state_machine_nesting]: >>> GOT DATA! x = hello
    [  INFO ] : State machine terminating 'GET':'got_it':'done'
    [  INFO ] : State machine terminating 'NESTED':'done':'succeeded'
    [INFO] [smach_example_state_machine_nesting]: Returned outcome: succeeded

"""

import rclpy
import rclpy.logging
from rclpy.node import Node
import smach


# Define a state to set some user data
class Setter(smach.State):
    def __init__(self, node: Node, val: str):
        smach.State.__init__(self, outcomes=["set_it"], output_keys=["x"])
        self._val = val
        self.logger = node.get_logger()

    def execute(self, ud):
        # Set the data
        ud.x = self._val
        self.logger.info(">>> Set data: %s" % str(self._val))
        return "set_it"


# Define a state to get some user data
class Getter(smach.State):
    def __init__(self, node: Node):
        smach.State.__init__(self, outcomes=["got_it"], input_keys=["x"])
        self.logger = node.get_logger()
        self.rate = node.create_rate(1 / 0.5)

    def execute(self, ud):
        # Wait for data to appear
        while "x" not in ud:
            self.logger.info(">>> Waiting for data...")
            self.rate.sleep(0.5)
        self.logger.info(">>> GOT DATA! x = " + str(ud.x))
        return "got_it"


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = Node("smach_example_state_machine_nesting")
    logger = node.get_logger()

    # Create a SMACH state machine
    sm0 = smach.StateMachine(outcomes=["succeeded"])

    # Open the container
    with sm0:
        # Add states to the container
        smach.StateMachine.add("SET", Setter(node, val="hello"), {"set_it": "NESTED"})

        sm1 = smach.StateMachine(outcomes=["done"], input_keys=["x"])
        smach.StateMachine.add("NESTED", sm1, {"done": "succeeded"})
        with sm1:
            smach.StateMachine.add("GET", Getter(node), {"got_it": "done"})

    # Execute SMACH plan
    outcome = sm0.execute()
    logger.info(f"Returned outcome: {outcome}")


if __name__ == "__main__":
    main()
