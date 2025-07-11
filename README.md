# Flask Backend

This directory contains a minimal Flask implementation of the API used by the React frontend.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
python -m flask_backend.app
```

The API exposes `/api/tables/<name>` which returns up to 100 rows from the specified table.

If the environment variable `KEYCLOAK_REALM` is set, requests are validated
against a Keycloak server. Configure `KEYCLOAK_URL`, `KEYCLOAK_CLIENT_ID` and
`KEYCLOAK_CLIENT_SECRET` accordingly.

## Using MariaDB

The backend works with a MariaDB database. A convenient way to start a local
server is using Docker:

```bash
docker run --name mci-mariadb -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=mci -p 3306:3306 -d mariadb
```

Set the following environment variables for the Flask app:

```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=root
export DB_NAME=mci
```

With the database running, start the server as shown above.
