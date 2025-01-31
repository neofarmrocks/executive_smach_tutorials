#!/usr/bin/env python3

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
        RosState.__init__(self, node, outcomes=["outcome1"])
        self.logger = node.get_logger()

    def execute(self, userdata: smach.UserData) -> str:
        self.logger.info("Executing state BAR")
        return "outcome1"


# define state Bas
class Bas(RosState):
    def __init__(self, node: Node) -> None:
        RosState.__init__(self, node, outcomes=["outcome3"])
        self.logger = node.get_logger()

    def execute(self, userdata: smach.UserData) -> str:
        self.logger.info("Executing state BAS")
        return "outcome3"


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = SmachNode("smach_example_state_machine")
    logger = node.get_logger()
    node.start()

    # Create the top level SMACH state machine
    sm_top = smach.StateMachine(outcomes=["outcome6"])

    # Open the container
    with sm_top:
        smach.StateMachine.add("BAS", Bas(node), transitions={"outcome3": "CON"})

        # Create the sub SMACH state machine
        sm_con = smach.Concurrence(
            outcomes=["outcome4", "outcome5"],
            default_outcome="outcome4",
            outcome_map={"outcome5": {"FOO": "outcome2", "BAR": "outcome1"}},
        )

        # Open the container
        with sm_con:
            # Add states to the container
            smach.Concurrence.add("FOO", Foo(node))
            smach.Concurrence.add("BAR", Bar(node))

        smach.StateMachine.add(
            "CON",
            sm_con,
            transitions={"outcome4": "CON", "outcome5": "outcome6"},
        )

    # Execute SMACH plan
    outcome = sm_top.execute()
    logger.info(f"Returned outcome: {outcome}")


if __name__ == "__main__":
    main()
