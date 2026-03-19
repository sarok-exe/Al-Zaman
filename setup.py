from setuptools import setup

setup(
    name="alzaman",
    version="1.0",
    description="Digital clock with Hijri date and country switcher",
    author="Your Name",
    py_modules=["alzaman"],
    install_requires=[
        "pytz",
        "hijri-converter",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "alzaman=alzaman:main",
        ],
    },
)
