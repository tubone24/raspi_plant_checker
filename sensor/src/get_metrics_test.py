from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import requests
from datetime import datetime, timedelta, timezone
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), "../../", '.env')
load_dotenv(dotenv_path)

RASPI_URL = os.environ.get("RASPI_URL")
HASURA_URL = os.environ.get("HASURA_URL")


def get_metrics_to_hasura():
    client = Client(
        transport=RequestsHTTPTransport(
            url=HASURA_URL,
            use_json=True,
            headers={
                "Content-type": "application/json",
            },
            retries=3,
        ),
        fetch_schema_from_transport=True,
    )
    query = gql(
        """
        query MyQuery {
            raspi_plant_checker {
              id
              light
              moisture
              timestamp
            }
        }
        """
    )
    result = client.execute(query)
    print(result)


def main():
    get_metrics_to_hasura()


if __name__ == "__main__":
    main()
