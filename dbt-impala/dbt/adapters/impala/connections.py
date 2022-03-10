from contextlib import contextmanager
from dataclasses import dataclass

import time
import dbt.exceptions

from dbt.adapters.base import Credentials
from dbt.adapters.sql import SQLConnectionManager

from typing import Optional, Tuple, Any

from dbt.contracts.connection import Connection, AdapterResponse

from dbt.events.functions import fire_event
from dbt.events.types import ConnectionUsed, SQLQuery, SQLQueryStatus

from dbt.logger import GLOBAL_LOGGER as logger

import impala.dbapi

DEFAULT_IMPALA_PORT = 21050

@dataclass
class ImpalaCredentials(Credentials):
    host: str
    port: int = DEFAULT_IMPALA_PORT
    username: Optional[str] = None
    password: Optional[str] = None
    schema: str
    database: str

    _ALIASES = {
        'dbname':'database',
        'pass':'password',
        'user':'username'
    }

    @property
    def type(self):
        return 'impala'

    def _connection_keys(self):
        # return an iterator of keys to pretty-print in 'dbt debug'.
        # Omit fields like 'password'!
        return ('host', 'port', 'database', 'schema', 'username')

    @property
    def unique_field(self) -> str:
        # adapter anonymous adoption
        return self.host


class ImpalaConnectionManager(SQLConnectionManager):
    TYPE = 'impala'

    @contextmanager
    def exception_handler(self, sql: str):
        try:
            yield
        except impala.dbapi.DatabaseError as exc:
            logger.debug('dbt-imapla error: {}'.format(str(e)))
            raise dbt.exceptions.DatabaseException(str(exc))
        except Exception as exc:
            logger.debug("Error running SQL: {}".format(sql))
            raise dbt.exceptions.RuntimeException(str(exc))

    @classmethod
    def open(cls, connection):
        if connection.state == 'open':
            logger.debug('Connection is already open, skipping open.')
            return connection

        credentials = connection.credentials

        try:
            handle = impala.dbapi.connect(
                host=credentials.host,
                port=credentials.port,
            )
            connection.state = 'open'
            connection.handle = handle
        except:
            logger.debug("Connection error")
            connection.state = 'fail'
            connection.handle = None
            pass

        return connection

    @classmethod
    def get_response(cls, cursor):
        message = 'OK'
        return AdapterResponse(
            _message=message
        )

    def cancel(self, connection):
        connection.handle.close()

    def add_begin_query(self, *args, **kwargs):
        logger.debug("NotImplemented: add_begin_query")

    def add_commit_query(self, *args, **kwargs):
        logger.debug("NotImplemented: add_commit_query")

    def commit(self, *args, **kwargs):
        logger.debug("NotImplemented: commit")

    def rollback(self, *args, **kwargs):
        logger.debug("NotImplemented: rollback")

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False
    ) -> Tuple[Connection, Any]:
        
        connection = self.get_thread_connection()
        if auto_begin and connection.transaction_open is False:
            self.begin()
        fire_event(ConnectionUsed(conn_type=self.TYPE, conn_name=connection.name))

        with self.exception_handler(sql):
            if abridge_sql_log:
                log_sql = '{}...'.format(sql[:512])
            else:
                log_sql = sql

            fire_event(SQLQuery(conn_name=connection.name, sql=log_sql))
            pre = time.time()

            cursor = connection.handle.cursor()

            # paramstlye parameter is needed for the datetime object to be correctly qouted when
            # running substitution query from impyla. this fix also depends on a patch for impyla:
            # https://github.com/cloudera/impyla/pull/486
            configuration = {}
            configuration['paramstyle'] = 'format'
            cursor.execute(sql, bindings, configuration)

            fire_event(
                SQLQueryStatus(
                    status=str(self.get_response(cursor)),
                    elapsed=round((time.time() - pre), 2)
                )
            )

            return connection, cursor