# Globerce delivery backend services


## Requirements

The project requires the following system packages:
```
postgresql-12
postgresql-server-12
```

## Installation

This section is under development.


## DB migrations
 
For developing it's required to make and upgrade migrations with `aerich` tool.
Each `Tortoise` table class has it's own schema. `aerich` has it's own table for keeping and watching migrations data.
Updating schemas must be followed by new migration and optional upgrade within migrations folder where `aerich.ini` file is stored.
Give new migrations consistent and concrete names only related to the changes.
```
aerich migrate --name <name_for_migration>
aerich upgrade
```


## Make

Few options available via Makefile usage within Docker container or local venv:

To check code for errors use:
```
make lint
```

To force imports sorting use:
```
make isort
```

To run tests:
```
make test
```


## Testing

Via docker-compose using 

```
docker-compose run --name api --rm -it --network host globerce/api bash -c "make test"
```

Standard approach to make functional testing for all tests within the project main directory:
```
python -m pytest
```

To make a test run without default config file usage simply use:
```
pytest -vv -c /dev/null test.py
```


With the same options but for a single test function:
```
pytest -vv -c /dev/null test.py::test_function_name
```


## Debugging
1. Open delivery/delivery folder as a Pycharm project.
2. Create poetry virtualenv, install packages from pyproject.toml file.
3. In the terminal run the command bellow:
   
```docker run -p 5432:5432 --name delivery_postgres_1 -e POSTGRES_USER=delivery -e POSTGRES_PASSWORD=delivery -e POSTGRES_DB=delivery -v postgresql:/var/lib/postgresql/data postgres:12.6```

4. Open Run/Debug Configurations on Pycharm.
5. Choose Python.
6. ScriptPath: ```delivery/delivery/api/__main__.py```
