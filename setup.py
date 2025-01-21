from setuptools import find_packages, setup

package_name = "smach_tutorials"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    author="Jonathan Bohren",
    maintainer="Robert Haschke",
    maintainer_email="rhaschke@techfak.uni-bielefeld.de",
    keywords=["ROS", "SMACH"],
    description="This package contains numerous examples of how to use SMACH. See the examples directory.",
    license="BSD",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [],
    },
)
