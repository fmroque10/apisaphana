import os



from dotenv import load_dotenv

from hdbcli import dbapi





load_dotenv()





def get_connection():

    return dbapi.connect(

        address=os.getenv("HANA_HOST"),

        port=int(os.getenv("HANA_PORT")),

        user=os.getenv("HANA_USER"),

        password=os.getenv("HANA_PASSWORD"),

        databaseName=os.getenv("HANA_DATABASE")

    )
