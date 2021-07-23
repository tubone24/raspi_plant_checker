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
HASURA_SECRET = os.environ.get("HASURA_SECRET")


def get_metrics(url: str):
    moisture = requests.get(url=f"{url}/moisture").json()
    light = requests.get(url=f"{url}/light").json()
    return {"moisture": moisture["value"], "light": light["value"]}


def upload_metric_to_hasura(moisture, light):
    client = Client(
        transport=RequestsHTTPTransport(
            url=HASURA_URL,
            use_json=True,
            headers={
                "Content-type": "application/json",
                "x-hasura-admin-secret": HASURA_SECRET
            },
            retries=3,
        ),
        fetch_schema_from_transport=True,
    )
    query = gql(
        """
        mutation MyMutation ($light: numeric!, $moisture: numeric!){
            insert_raspi_plant_checker_one(object: {light: $light, moisture: $moisture}) {
                id
                light
                moisture
                timestamp
            }
        }
        """
    )
    params = {"light": light, "moisture": moisture}
    result = client.execute(query, variable_values=params)
    print(result)


def delete_old_metrics_to_hasura(days_before=7):
    dt_now = datetime.now(timezone.utc)
    before_day = dt_now - timedelta(days=days_before)
    dt = before_day.astimezone().isoformat(timespec='microseconds')
    client = Client(
        transport=RequestsHTTPTransport(
            url=HASURA_URL,
            use_json=True,
            headers={
                "Content-type": "application/json",
                "x-hasura-admin-secret": HASURA_SECRET
            },
            retries=3,
        ),
        fetch_schema_from_transport=True,
    )
    query = gql(
        """
        mutation MyMutation ($dt: timestamptz){
            delete_raspi_plant_checker(where: {timestamp: {_lt: $dt}}) {
                returning {
                    id
                    light
                    moisture
                    timestamp
                }
            }
        }
        """
    )
    params = {"dt": dt}
    result = client.execute(query, variable_values=params)
    print(result)


def main():
    metrics = get_metrics(RASPI_URL)
    upload_metric_to_hasura(moisture=metrics["moisture"], light=metrics["light"])
    delete_old_metrics_to_hasura()


if __name__ == "__main__":
    main()
