#!/usr/bin/env python3
"""
Description:

Usage:
    $> ./state_machine_simple_introspection.py


Output:
    [INFO] [1737454917.170229337] [smach_ros]: State machine starting in initial state 'FOO' with userdata:
            []
    [INFO] [1737454917.170646969] [smach_example_state_machine]: Executing state FOO
    [INFO] [1737454917.171106609] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [1737454917.171507811] [smach_example_state_machine]: Executing state BAR
    [INFO] [1737454917.171915033] [smach_ros]: State machine transitioning 'BAR':'outcome2'-->'FOO'
    [INFO] [1737454917.172238298] [smach_example_state_machine]: Executing state FOO
    [INFO] [1737454917.172658235] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [1737454917.172977763] [smach_example_state_machine]: Executing state BAR
    [INFO] [1737454917.173379225] [smach_ros]: State machine transitioning 'BAR':'outcome2'-->'FOO'
    [INFO] [1737454917.173702340] [smach_example_state_machine]: Executing state FOO
    [INFO] [1737454917.174114141] [smach_ros]: State machine transitioning 'FOO':'outcome1'-->'BAR'
    [INFO] [1737454917.174440292] [smach_example_state_machine]: Executing state BAR
    [INFO] [1737454917.174852343] [smach_ros]: State machine transitioning 'BAR':'outcome2'-->'FOO'
    [INFO] [1737454917.175165129] [smach_example_state_machine]: Executing state FOO
    [INFO] [1737454917.175607307] [smach_ros]: State machine terminating 'FOO':'outcome2':'outcome4'
    [INFO] [1737454917.175903922] [smach_example_state_machine]: Returned outcome: outcome4

Watch:
    $> ros2 topic echo /my_smach_introspection_server/smach/container_init
    $> ros2 topic echo /my_smach_introspection_server/smach/container_status
    $> ros2 topic echo /my_smach_introspection_server/smach/container_structure
"""

import rclpy
import rclpy.logging
from rclpy.node import Node
import smach
from smach_ros import (
    IntrospectionServer,
    RosState,
    SmachNode,
)


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

    def execute(self, userdata: smach.UserData) -> str:
        self.logger.info("Executing state BAR")
        return "outcome2"


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

    # Create and start the introspection server
    sis = IntrospectionServer("my_smach_introspection_server", sm, "/SM_ROOT")
    sis.start()

    # Execute SMACH plan
    outcome = sm.execute()
    logger.info(f"Returned outcome: {outcome}")

    # Wait for ctrl-c to stop the application
    rclpy.spin(node)
    sis.stop()


if __name__ == "__main__":
    main()
