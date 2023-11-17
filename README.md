<h1 style="text-align: center;">tcex - Table Content EXporter</h1>

## Table of Contents

- [Introduction](#introduction)
- [Set up](#setup)
- [Run](#run)




## Introduction

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

With this little tool you can connect to a MySQL database server and select tables from a 
specific schema to be exported as CSV files.

## Setup

#### Virtual Environment

Create virtual environment and install dependencies (requirements)

```shell
$ virtualenv --python=python3.9 venv
$ source venv/bin/activate
(venv) $ pip3 install -r requirements.txt
```

#### Environment variables

To specify the location of the database server the application reads environment variables which
you can provide either via shell variables or initializing in a `.env` (in the working directory).

THe supported variables are:

- **TCEX_HOSTNAME**: the host address of the server 
- **TCEX_USERNAME**: the user to connect to the server 
- **TCEX_PASSWORD**: the user's password
- **TCEX_DATABASE**: the database (schema) from which you wish to export the tables from

## Run

```shell
(venv) $ python3 app/main.py
```
