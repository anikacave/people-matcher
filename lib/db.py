from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.exc import OperationalError
import time


base = declarative_base()
PG_USER = os.environ.get("PG_USER")
PG_PW = os.environ.get("PG_PW")
PG_HOST = os.environ.get("PG_HOST")
PG_PORT = os.environ.get("PG_PORT", 5432)
PG_DB = os.environ.get("PG_DB")
db_string = "postgres://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}".format(
    PG_USER=PG_USER, PG_PW=PG_PW, PG_HOST=PG_HOST, PG_PORT=PG_PORT, PG_DB=PG_DB
)
print(db_string)
db = create_engine(db_string)


def get_session():
    Session = sessionmaker(db)
    return Session()


class GeocodeResult(base):

    __tablename__ = "geocode_results"
    input_hash = Column(String, primary_key=True)
    output = Column(JSON)
    sess = get_session()

    def get(self, input_args):
        input_hash = self.hash(input_args)
        for obj in self.sess.query(GeocodeResult).filter(
            GeocodeResult.input_hash == input_hash
        ):
            return obj.output
        return None

    def hash(self, input_args):
        return str(input_args)

    def set(self, input_args, output):
        input_hash = self.hash(input_args)
        obj = GeocodeResult(input_hash=input_hash, output=output)
        self.sess.add(obj)
        self.sess.commit()


def init_db():
    try:
        base.metadata.create_all(db)
    except OperationalError:
        time.sleep(3)
        print("Waiting 3 seconds for the database to start up.")
        base.metadata.create_all(db)


if __name__ == "__main__":
    init_db()
