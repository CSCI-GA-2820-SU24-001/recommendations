# NYU DevOps: Recommendations
[![Build Status](https://github.com/CSCI-GA-2820-SU24-001/recommendations/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU24-001/recommendations/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU24-001/recommendations/graph/badge.svg?token=JSCK57Z84T)](https://codecov.io/gh/CSCI-GA-2820-SU24-001/recommendations)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

CSCI-GA.2820-003 DevOps and Agile Methodologies Summer 2024

## Overview

This project aims to provide recommendations for customers based on their purchase histories. It will become a part of an e-commerce website.

## Setup

1. open Terminal at your project document

2. start Docker

3. clone our repo

   ```
   $ git clone git@github.com:CSCI-GA-2820-SU24-001/recommendations.git
   $ cd recommendations
   ```

4. choose "reopen in Docker container" in VSCode

5. Finally open Terminal: 

   ```python
   flask run
   ```



## Manually running the Tests

If you did not install this, you should first install `coverage`

```
pip install coverage
```

This repo also has unit tests that you can run

```
coverage run -m pytest
```



## API Calls Setting in this service

```
GET  /recommendations - Returns all of the Recommendations
GET  /recommendations/{id} - Retrieves a recommendation with a specific id
POST /recommendations - Creates a recommendation in the database from the posted data
DELETE /recommendations/{id} - Deletes a recommendation from the database that matches the id
```



## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```
