import datetime
import os
import re
import struct
import sys
import warnings
from math import floor, isinf
from time import time
import subprocess
import json

import numpy as np
import pandas as pd
import pyodbc
from azure.identity import AzureCliCredential
from ds import clean
from ds.paths import Paths
from ds.utils import get_os, menu_input
from requests import Session


class ConnectDatabase:

    """
    Connect & Query Databases

    Tools to help connect to and query databases

    Parameters:
        credentials: A named set of credentials (i.e., the named attribute from a config object) as read by ds.connect's Config class
        other: Additional semicolon separated elements to add to the end of the connection string; defaults to ';ApplicationIntent=ReadOnly'
        token: A Boolean value, True (default) means that the Azure CLI will be utilized to generate a token (required for use on Mac).  If False, then multi-factor authentication is utilized.
        path: A path to a local Microsoft Access database (Windows only)

    Attributes:
        credentials: The credentials passed into the class saved for later
        connection_string: The connection string made for connecting

    Methods:
        as_create_sql_table: Convert a pandas DataFrame to tsql query (as a string) to add a table to a database
        as_declare_sql_table: Convert a pandas DataFrame to tsql query (as a string) to use a table as an @ object within a sql query
        as_sql_list: Convert a Python list to a string for use in tsql
        check: A check to ensure the connection is still good
        close: Close the established connection
        count: A method to generate aggregated counts (including NULLS) of an enumerated column.  To create, supply the args `name` (table name as a string) and `column` (enumerated field as a string)
        database: A method to report the database that is connected
        delete_table: A method to delete tables from a data base, simply supply `name` as a string for the table name
        describe: A method to give the sizes of the tables in a database
        fake_institutions: Generate a list of known fake institution IDs
        get: A method to extract tables from the database.  Use the argument `n = ` to get the top n rows
        nrow: Get the number of rows for a table
        columns: get the names of columns for a table as a list (if `name = None` then all tables and columns are returned as a table)
        get_random: Get n random rows for a table
        is_open: A method to report if the connection is closed
        lookup_schema_name: A function to return the schema name given the table name
        query: A method to query the data base directly with sql code
        search: A method to list all the tables and column names that contain a search term.  Use the argument `term = ` to specify the search term
        server: A method to report the server to which the database is located
        tables: A method to list valid (1) base and (2) view tables that can be queried via `.get()`
        variables: A method to give the of all tables in the data base database or a specific table if `name` is not missing
        write_table: A method to add, append, or overwrite tables.  To create, supply the args `dataframe` (Pandas DataFrame) and `name` (table name as a string).  One can also use `append = True` and overwrite = `True`

    Examples::

        from ds.connect import ConnectDatabase, Config

        crds = Config()
        bdb = ConnectDatabase(crds.beacon)

        bdb.check()
        bdb.tables()
        bdb.get('StudentFile', n=100)
        bdb.search('student')
        bdb.count('StudentFile', 'AudienceType')
        bdb.as_sql_list(['d', 'don\'t do it'])

        pdb = ConnectDatabase(crds.publicdata)
        pdb.fake_institutions()
        pdb.database()

        import pandas as pd
        iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
        pdb.write_table(iris, 'DeleteMeIris', append = True)
        pdb.tables()
        pdb.get('DeleteMeIris')
        pdb.delete_table('DeleteMeIris')


        idb = ConnectDatabase(crds.institutions)

        idb.tables()
        idb.get('Institution', n = 10).columns

        my_query = '''
        SELECT
            i.[Id],
            i.[IpedsId],
            i.[Name],
            i.[Address],
            i.[City],
            i.[State]
        FROM [dbo].[Institution] as i WITH (NOLOCK)
        WHERE Deleted = 0 AND
        Id IN {fakes}
        '''.format(fakes=idb.fake_institutions())

        print(my_query)


        fakes = idb.query(my_query)
        fakes
    """

    def __init__(
        self,
        credentials=None,
        other: str = ";ApplicationIntent=ReadOnly",
        token: bool = True,
        path: str = None,
    ):

        if credentials is not None:
            self.credentials = credentials
            expected = [
                "ServerName",
                "Auth",
                "User",
                "Password",
                "Database",
                "Driver",
                "SourceType",
            ]
            actual = list(self.credentials.keys())
            checks = {elem: elem in actual for elem in expected}
            if not all(checks.values()):
                missing = ", ".join(
                    ["'{}'".format(k) for k, v in checks.items() if not v]
                )
                raise Exception(
                    "The following fields are missing from `credentials`: {}".format(
                        missing
                    )
                )
            if (len(other) > 0) and (other[0] != ";"):
                raise Exception(
                    "`other` must be a series of authentication arguments starting with, and separated by, semicolons"
                )

            else:

                if (token) or (get_os() == "Mac"):

                    expected = ["ServerName", "Database", "Driver", "TenantId"]
                    actual = list(self.credentials.keys())
                    checks = {elem: elem in actual for elem in expected}
                    if not all(checks.values()):
                        missing = ", ".join(
                            ["'{}'".format(k) for k, v in checks.items() if not v]
                        )
                        raise Exception(
                            "The following fields are missing from `credentials`: {}".format(
                                missing
                            )
                        )

                    self.tenant = re.sub(
                        "^.+@|\\.com$", "", self.credentials["User"]
                    ).lower()

                    print("Using Stored Credentials & Obtaining Token", flush=True)

                    self.token = _DataBaseCredentialWrapper(
                        tenant=self.tenant, tenantid=self.credentials.get("TenantId")
                    )
                    tokenstruct = _prepare_token(self.token)

                    # build connection string using acquired token
                    self.connection_string = _Hidden_Password_String(
                        "DRIVER={};SERVER={};DATABASE={}".format(
                            "{" + self.credentials["Driver"] + "}",
                            self.credentials["ServerName"],
                            self.credentials["Database"],
                        )
                        + other
                    )

                    SQL_COPT_SS_ACCESS_TOKEN = 1256
                    self.connection = pyodbc.connect(
                        self.connection_string,
                        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: tokenstruct},
                    )
                    self.connection_type = "Token"
                    self.other = other

                else:

                    expected = [
                        "ServerName",
                        "Auth",
                        "User",
                        "Password",
                        "Database",
                        "Driver",
                    ]
                    actual = list(self.credentials.keys())
                    checks = {elem: elem in actual for elem in expected}
                    if not all(checks.values()):
                        missing = ", ".join(
                            ["'{}'".format(k) for k, v in checks.items() if not v]
                        )
                        raise Exception(
                            "The following fields are missing from `credentials`: {}".format(
                                missing
                            )
                        )

                    print(
                        "Using Stored Credentials & Windows MFA...\n\nLook for a browser dialogue window to authenticate",
                        flush=True,
                    )
                    self.connection_string = _Hidden_Password_String(
                        "DRIVER={};SERVER={};DATABASE={};UID={};PWD={};AUTHENTICATION={}".format(
                            "{" + self.credentials["Driver"] + "}",
                            self.credentials["ServerName"],
                            self.credentials["Database"],
                            self.credentials["User"],
                            self.credentials["Password"],
                            self.credentials["Auth"],
                        )
                        + other
                    )

                    self.connection = pyodbc.connect(self.connection_string)
                    self.connection_type = "MFA"

                # self.connection.timeout = 0
                self.cursor = self.connection.cursor()

        elif (path is not None) and (get_os() == "Windows"):

            self.credentials = {"Path": path, "SourceType": "Local Database"}
            self.path = path
            if not os.path.exists(path):
                raise Exception("`path` does not seem to exist")

            self.connection_string = (
                r"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={};".format(
                    self.path
                )
            )
            self.connection = pyodbc.connect(self.connection_string)
            self.connection_type = "Local Database"
            self.cursor = self.connection.cursor()

        else:
            raise Exception("No `credentials` or `path` (Windows only) supplied")

    def __repr__(self):
        return "\n" + "\n".join(
            [
                "{}: {}".format(i, "*****" if i == "Password" else j)
                for i, j in self.credentials.items()
            ]
        )

    def test_token(self):

        if (self.connection_type == "Token") and (
            time() > self.token.cli_token.expires_on - 100
        ):

            print(
                "Getting new Access Token\nUsing Stored Credentials & Obtaining Token",
                flush=True,
            )

            self.token = _DataBaseCredentialWrapper(
                tenant=self.tenant, tenantid=self.credentials.get("TenantId")
            )
            tokenstruct = _prepare_token(self.token)

            SQL_COPT_SS_ACCESS_TOKEN = 1256
            self.connection = pyodbc.connect(
                self.connection_string,
                attrs_before={SQL_COPT_SS_ACCESS_TOKEN: tokenstruct},
            )

    def check(self):
        self.test_token()
        try:
            cursor = self.connection.cursor()
            # print("Connection Appears Open", flush=True)
        except Exception as e:
            if e.__class__ == pyodbc.ProgrammingError:
                warnings.warn("Connection Has Been Closed")

    def close(self):
        self.test_token()
        self.cursor.close()
        self.connection.close()
        try:
            cursor = self.connection.cursor()
        except Exception as e:
            cursor = None
        else:
            warnings.warn("Connection seems to be open still")

    ##def timeout(self, timeout:int = 0):
    ##
    ##    self.connection.timeout = timeout
    ##    self.cursor = self.connection.cursor()

    def query(self, query=None, results=True):

        self.check()

        if query is None:
            query = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE IN ('BASE TABLE', 'VIEW') AND TABLE_SCHEMA NOT IN ('sys')"

        if results is True:
            # print("Returning Results", flush=True)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dat = pd.read_sql_query(query, self.connection)
            return dat
        else:
            # print("No results returned", flush=True)
            self.connection.cursor().execute(query)
            self.connection.commit()

    def is_open(self):
        try:
            x = self.tables()
        except Exception as e:
            if e.__class__ == pyodbc.ProgrammingError:
                warnings.warn("Connection Has Been Closed")
            else:
                print("Connection Appears Open", flush=True)

    def database(self):
        return self.query(query="SELECT DB_NAME() AS ThisDB;")

    def server(self):
        return self.query(
            query="SELECT CONCAT(CONVERT(nvarchar(50),SERVERPROPERTY('ServerName')),'.database.windows.net') as FullServerName;"
        )

    def get(self, name, n=float("inf")):
        return self.query(
            "SELECT {} * FROM {} WITH (NOLOCK)".format(
                "" if isinf(n) else "TOP ({}) ".format(n), name
            )
        )

    def nrow(self, name):
        return self.query(
            "SELECT sum([rows]) FROM sys.partitions WHERE object_id=object_id('{}') AND index_id in (0,1)".format(
                name
            )
        )

    def columns(self, name: str = None):

        if name is None:
            return self.query(
                """
            SELECT schema_name(tab.schema_id) as schema_name,
                tab.name as table_name, 
                    col.column_id,
                    col.name as column_name, 
                    t.name as data_type,    
                    col.max_length,
                    col.precision
                FROM sys.tables as tab
                    INNER JOIN sys.columns as col
                        ON tab.object_id = col.object_id
                    LEFT JOIN sys.types as t
                    ON col.user_type_id = t.user_type_id
                ORDER BY schema_name,
                    table_name, 
                    column_id;
            """
            )
        else:
            return list(self.query("SELECT TOP 0 * FROM [{}]".format(name)).columns)

    def get_random(self, name, n: int):
        nr = self.nrow(name).iloc[0, 0]
        if n > nr:
            raise Exception(
                "`n` can not be greater than number of rows in '{}' (n = {})".format(
                    name, "{:,}".format(nr)
                )
            )

        colnm = self.columns(name)[0]

        rows = self._random_rows_as_sql_list(n, nr)

        return self.query(
            "WITH myTableWithRows AS (SELECT (ROW_NUMBER() OVER (ORDER BY [{}])) as RowNumber,* FROM {} ) SELECT * FROM myTableWithRows WHERE RowNumber IN {}".format(
                colnm, name, rows
            )
        )

    def _random_rows_as_sql_list(self, n, size):

        rows = []
        while len(rows) < n:
            val = np.random.randint(1, size + 1)
            if val not in rows:
                rows.append(val)

        return self.as_sql_list(np.sort(rows))

    def tables(self, to_list: bool = False):
        if to_list:
            return self.query("SELECT * FROM information_schema.tables;")[
                "TABLE_NAME"
            ].to_list()
        else:
            return self.query("SELECT * FROM information_schema.tables;")

    def list_tables(self):
        if self.connection_type == "Local Database":
            return [row.table_name for row in self.cursor.tables()]
        else:
            return list(self.tables()["TABLE_NAME"])

    def lookup_schema_name(self, table):
        return (
            self.tables()[["TABLE_SCHEMA", "TABLE_NAME"]]
            .set_index("TABLE_NAME", inplace=False)
            .to_dict()["TABLE_SCHEMA"][table]
        )

    def search(self, term):

        search_query = " ".join(
            [
                "SELECT COLUMN_NAME, TABLE_NAME, TABLE_SCHEMA",
                "FROM INFORMATION_SCHEMA.COLUMNS",
                "WHERE COLUMN_NAME LIKE '%" + term + "%' ",
            ]
        )

        return self.query(search_query)

    def count(self, table, column, decreasing=True, where=None):

        if decreasing:
            order = "desc"
        else:
            order = ""

        if where is not None:
            where = " ".join(["AND", where])
        else:
            where = ""

        count_query = "\n".join(
            [
                "(SELECT",
                "    [{}]",
                "    ,COUNT([{}]) as n",
                "  FROM {}",
                "  WHERE [{}] IS NOT NULL {}",
                "  GROUP BY [{}]",
                ")",
                "",
                "UNION",
                "",
                "(SELECT ",
                "    'NULL' as [{}], ",
                "    COUNT(*) as n",
                "  FROM {}",
                "  WHERE [{}] IS NULL {}",
                ")",
                "",
                "  ORDER BY n {}",
            ],
        ).format(
            column,
            column,
            table,
            column,
            where,
            column,
            column,
            table,
            column,
            where,
            order,
        )

        return self.query(count_query)

    def as_sql_list(self, x: list):
        return (
            "("
            + ", ".join(["'" + re.sub("(?<!')'(?!')", "''", str(i)) + "'" for i in x])
            + ")"
        )

    def as_declare_sql_table(
        self,
        dataframe,
        name: str = "@mytable",
        break_length: int = 1000,
        command: str = "DECLARE",
        command2: str = "TABLE",
        additional: str = "",
        nullable: list = [True],
    ):

        out = _make_sql_table_query(
            dataframe,
            name=name,
            break_length=break_length,
            command=command,
            command2=command2,
            additional=additional,
            nullable=nullable,
        )

        return out

    def as_create_sql_table(
        self,
        dataframe,
        name: str = "mytable",
        break_length: int = 1000,
        command: str = "CREATE TABLE",
        command2: str = "",
        additional: str = "",
        nullable: list = [True],
    ):

        out = _make_sql_table_query(
            dataframe,
            name=name,
            break_length=break_length,
            command=command,
            command2=command2,
            additional=additional,
            nullable=nullable,
        )

        return out

    def fake_institutions(self, as_sql_list: bool = True):
        return clean.fake_institutions(as_sql_list=as_sql_list)

    def delete_table(self, name):

        if not self._has_permission(operation="DROP TABLE"):
            return
        elif name not in self.tables(to_list=True):
            warnings.warn("`{}` does appear to be in the database?".format(name))

            ans = menu_input(
                ["Yes", "No"],
                "You are about to delete the table `{}`; Do you want to continue?".format(
                    name
                ),
            )
            if ans == "No":
                raise Exception("Aborting table deletion")
            else:
                tabs = self.tables()
                query = "DROP TABLE [{}].[{}].[{}];".format(
                    self.database().iloc[0, 0], self.lookup_schema_name(name), name
                )
                cursor = self.connection.cursor()
                cursor.execute(query)
                cursor.commit()

            if name in self.tables(to_list=True):
                warnings.warn("`{}` does not appear to have deleted!".format(name))

    def write_schema(self, dataframe, name, overwrite: bool = False):

        self.test_token()
        found = name in self.tables(to_list=True)

        if re.search(" ", dataframe.columns):
            raise Exception(
                "Aborting write because `{}` contained a column header with a space".format(
                    name
                )
            )

        if overwrite and found:
            self.delete_table(name)
            if name in self.tables(to_list=True):
                raise Exception(
                    "Aborting write because `overwrite = True` but `{}` could not be deleted".format(
                        name
                    )
                )

        cursor = self.connection.cursor()

        write_query = _make_sql_schema_query(
            dataframe=dataframe,
            name=name,
            command="CREATE TABLE",
            command2="",
            additional="",
            nullable=[True],
        )

        self.connection.cursor().execute(write_query)
        self.connection.commit()

        if name not in self.tables(to_list=True):
            warnings.warn("`{}` does not appear to have written!".format(name))

    def write_table(
        self,
        dataframe,
        name,
        overwrite: bool = False,
        append: bool = False,
        break_length: int = 1000,
        batch_size: int = 200000,
        verbose: bool = True,
    ):

        if verbose:
            jobstart = datetime.datetime.now()
            print("Upload Start: {}".format(jobstart.strftime("%I:%M:%S %p")))
            sys.stdout.flush()

        self.test_token()

        if not self._has_permission("CREATE TABLE"):
            return
        else:

            found = name in self.tables(to_list=True)

            if (not found) and append:
                raise Exception(
                    "Aborting write because `{}` not found int he database but `append = True`".format(
                        name
                    )
                )

            if overwrite and found:
                self.delete_table(name)
                if name in self.tables(to_list=True):
                    raise Exception(
                        "Aborting write because`overwrite = True` but `{}` could not be deleted".format(
                            name
                        )
                    )

            if not append:

                cursor = self.connection.cursor()

                write_query = _make_sql_schema_query(
                    dataframe=dataframe,
                    name=name,
                    command="CREATE TABLE",
                    command2="",
                    additional="",
                    nullable=[True],
                )

                self.connection.cursor().execute(write_query)
                self.connection.commit()

                if name not in self.tables(to_list=True):
                    warnings.warn("`{}` does not appear to have written!".format(name))

                cursor.close()

                append = True

            if append:

                existing = list(self.get(name, n=1).columns)
                prior = self.query("SELECT COUNT(*) as N FROM {};".format(name)).iloc[
                    0, 0
                ]
                new = list(dataframe.columns)
                if sum([0 for i, j in zip(existing, new) if i == j]) != 0:
                    raise Exception(
                        "Aborting because `dataframe` column names do not apprear to match the names in `{}`".format(
                            name
                        )
                    )

                ## rows = _make_sql_table_rows_query(dataframe = dataframe, name = name, break_length = break_length)
                ## self.connection.cursor().execute(rows)
                ## self.connection.commit()

                ## indat = dataframe.shape[0]
                ## cur = self.query("SELECT COUNT(*) as N FROM {};".format(name)).iloc[0,0]
                ## if (indat + prior != cur):
                ##     warnings.warn("`{}` has {} rows.  Expecting {}: {} previously plus {} new for `dataframe`".format    (name,  str(cur), str(indat + prior), str(prior), str(indat)))
                ## else:
                ##     print("`{}` appears to have been appended".format(name), flush=True)

                ## Force int to have no trailing decimal and/or zeros
                for i in dataframe.columns:
                    if dataframe[i].dtype == "int64":
                        dataframe[i] = [format(j, ".0f") for j in dataframe[i]]

                for i in dataframe.columns:
                    if dataframe[i].dtype == "bool":
                        dataframe[i] = [
                            "1" if j else 0 if ((not j) and (j is not None)) else None
                            for j in dataframe[i]
                        ]

                sql_statement = "INSERT INTO {} ({}) values({})".format(
                    name,
                    ", ".join(["[" + x + "]" for x in dataframe.columns]),
                    ", ".join(["?" for i in range(dataframe.shape[1])]),
                )

                start_sql = self.query(
                    "SELECT COUNT(*) as n FROM {}".format(name)
                ).iloc[0, 0]
                starts = [x for x in list(range(0, dataframe.shape[0], batch_size))]
                ends = list(range(batch_size, dataframe.shape[0], batch_size)) + [
                    dataframe.shape[0]
                ]

                # list_df = [dataframe[s:e].copy() for s, e in zip(starts, ends)]
                for i, s, e in zip(range(len(starts)), starts, ends):

                    ## Grab the batch chunk
                    df = dataframe[s:e].copy()
                    list_of_tuples = df.values.tolist()
                    ## Upload each batch
                    if verbose:
                        start = datetime.datetime.now()
                        print(
                            "\n"
                            + "    Batch {} of {} started at {}".format(
                                i + 1, len(starts), start.strftime("%I:%M:%S     %p")
                            )
                        )
                        sys.stdout.flush()
                        print(
                            "        Rows {} - {} of {}".format(
                                "{:,}".format(s + 1),
                                "{:,}".format(e),
                                "{:,}".format(dataframe.shape[0]),
                            )
                        )
                        sys.stdout.flush()

                    cursor = self.connection.cursor()
                    cursor.fast_executemany = True
                    cursor.executemany(sql_statement, list_of_tuples)
                    cursor.commit()
                    cursor.close()

                    ## Ensure the table is the expected size
                    now_sql = self.query(
                        "SELECT COUNT(*) as n FROM {}".format(name)
                    ).iloc[0, 0]
                    if (now_sql - start_sql) != e:
                        warnings.warn(
                            "The upload just uploaded up to row {}; started with {} but only {} found in the sql     table".format(
                                e, start_sql, now_sql
                            )
                        )

                    if verbose:
                        print(
                            "        Completed in {} minutes ({}% complete)".format(
                                round(
                                    (datetime.datetime.now() - start).total_seconds()
                                    / 60,
                                    1,
                                ),
                                round(100 * e / dataframe.shape[0], 1),
                            )
                        )
                        sys.stdout.flush()

        if verbose:
            print(
                "\n"
                + "Upload End: {}    {} minutes total".format(
                    start.strftime("%I:%M:%S %p"),
                    round((datetime.datetime.now() - jobstart).total_seconds() / 60),
                )
            )
            sys.stdout.flush()

    def variables(self, name=None):

        out = self.query("select * from information_schema.columns")
        tables = self.tables()
        out2 = pd.merge(
            out,
            tables["TABLE_NAME"],
            how="right",
            left_on=["TABLE_NAME"],
            right_on=["TABLE_NAME"],
        )

        if name is None:
            return out2
        else:
            return out2[out2["TABLE_NAME"] in name]

    def describe(self):

        describe_query = " ".join(
            [
                "SELECT  ",
                "",
                "    t.NAME AS TableName, ",
                "",
                "    s.Name AS SchemaName, ",
                "",
                "    p.rows AS RowCounts, ",
                "",
                "    SUM(a.total_pages) * 8 AS TotalSpaceKB,  ",
                "",
                "    CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS TotalSpaceMB, ",
                "",
                "    SUM(a.used_pages) * 8 AS UsedSpaceKB,  ",
                "",
                "    CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS UsedSpaceMB,  ",
                "",
                "    (SUM(a.total_pages) - SUM(a.used_pages)) * 8 AS UnusedSpaceKB, ",
                "",
                "    CAST(ROUND(((SUM(a.total_pages) - SUM(a.used_pages)) * 8) / 1024.00, 2) AS NUMERIC(36, 2)) AS UnusedSpaceMB ",
                "",
                "FROM  ",
                "",
                "    sys.tables t ",
                "",
                "INNER JOIN       ",
                "",
                "    sys.indexes i ON t.OBJECT_ID = i.object_id ",
                "",
                "INNER JOIN  ",
                "",
                "    sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id ",
                "",
                "INNER JOIN  ",
                "",
                "    sys.allocation_units a ON p.partition_id = a.container_id ",
                "",
                "LEFT OUTER JOIN  ",
                "",
                "    sys.schemas s ON t.schema_id = s.schema_id ",
                "",
                "WHERE  ",
                "",
                "    t.NAME NOT LIKE 'dt%'  ",
                "",
                "    AND t.is_ms_shipped = 0 ",
                "",
                "    AND i.OBJECT_ID > 255  ",
                "",
                "GROUP BY  ",
                "",
                "    t.Name, s.Name, p.Rows ",
                "",
                "ORDER BY  ",
                "",
                "    t.Name ",
            ]
        )

        return self.query(describe_query)

    def az_login(self):
        os.system("az login")

    def az_logout(self):
        os.system("az logout")

    def _has_permission(self, operation: str = "CREATE TABLE"):
        ret = self.query(
            f"SELECT HAS_PERMS_BY_NAME(db_name(), 'DATABASE', '{operation}')"
        )

        if ret.iloc[0, 0] != 1:
            print(f"You do not have permission for {operation}", flush=True)
            return False
        else:
            return True


class _Hidden_Password_String(str):
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return re.sub(
            r"(^.+?PWD=)(.+?)(;AUTHENTICATION=.+$)", r"\g<1>*****\g<3>", self.x
        )


## Helper function to make tables
def _make_sql_table_query(
    dataframe,
    name: str = "@mytable",
    break_length: int = 1000,
    command: str = "DECLARE",
    command2: str = "TABLE",
    additional: str = "",
    nullable: list = [True],
):

    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    dec_table = _make_sql_schema_query(
        dataframe=dataframe,
        name=name,
        command=command,
        command2=command2,
        additional=additional,
        nullable=nullable,
    )

    tab = _make_sql_table_rows_query(
        dataframe=dataframe, name=name, break_length=break_length
    )

    return "\n".join([dec_table, " ", tab, ""])


def _make_sql_schema_query(
    dataframe,
    name: str = "@mytable",
    command: str = "DECLARE",
    command2: str = "TABLE ",
    additional: str = "",
    nullable: list = [True],
):

    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    ## Make the type declaration (the schema)
    coltypes = {x: str(dataframe[x].dtype) for x in dataframe.columns}
    charcols = [
        k for k, v in coltypes.items() if np.isin(v, ["object", "string", "category"])
    ]
    if len(charcols) > 0:
        for x in charcols:
            dataframe[x] = dataframe[x].astype(str).str.replace("'", "''")

    coltypes = {x: str(dataframe[x].dtype) for x in dataframe.columns}

    lookup = dict(
        [
            (
                v,
                dataframe[v]
                .apply(lambda r: len(str(r)) if (r != None) else None)
                .max(),
            )
            for v in dataframe.columns.values
        ]
    )
    lookup = {
        k: str(int(v) + 200) if not pd.isnull(v) else None for k, v in lookup.items()
    }
    lookup = {
        k: (v if coltypes.get(k) == "object" else None) for k, v in lookup.items()
    }
    lookup = {
        k: v if (v is None) or (int(v) < 7000) else "Max" for k, v in lookup.items()
    }

    def sql_type(x):
        out = []
        for i in x:
            if i in ["float64", "float32"]:
                out.append("NUMERIC(32, 5)")
            elif i in ["int32", "int64"]:
                out.append("INT")
            elif i == "datetime64":
                out.append("DATETIME")
            elif i == "datetime64[ns]":
                out.append("DATETIME")
            elif i == "bool":
                out.append("INT")
            else:
                out.append("VARCHAR({})")

        return out

    types = sql_type(coltypes.values())
    types = [
        x.format(z) if z is not None else x for x, z in zip(types, lookup.values())
    ]

    if additional != "":
        "\n" + additional

    if len(nullable) == 1:
        nullable = [nullable[0] for i in range(len(types))]

    nn = []
    for i in range(len(nullable)):
        if nullable[i]:
            nn.append("")
        else:
            nn.append(" NOT NULL")

    nullable = nn

    dec_table = "{} {} {}(\n{}{}\n)".format(
        command,
        name,
        command2,
        ",\n".join(
            [
                "    [{}] {}{}".format(x, y, z)
                for x, y, z in zip(dataframe.columns, types, nullable)
            ]
        ),
        additional,
    )

    return dec_table


def _make_sql_table_rows_query(dataframe, name: str, break_length: int = 1000):

    if not isinstance(dataframe, pd.DataFrame):
        raise Exception("`dataframe` does not appear to be a Pandas DataFrame")

    ## Insert statement
    tab_insert = "REMOVEME123321insert into [{}] valuesDELETEME123321".format(name)

    ## Force int to have no trailing decimal and/or zeros
    for i in dataframe.columns:
        if dataframe[i].dtype == "int64":
            dataframe[i] = [format(j, ".0f") for j in dataframe[i]]

    for i in dataframe.columns:
        if dataframe[i].dtype == "bool":
            dataframe[i] = [
                "1" if j else 0 if ((not j) and (j is not None)) else None
                for j in dataframe[i]
            ]

    ## Concatenate rows
    rows = []
    for i in range(dataframe.shape[0]):
        rows.append(
            "("
            + ", ".join(
                [
                    "NULL" if pd.isnull(x) else "'" + str(x) + "'"
                    for x in dataframe.iloc[
                        i,
                    ]
                ]
            )
            + ")"
        )

    ## Insert the break
    if len(rows) > break_length:
        for i in range(break_length, len(rows) + break_length, break_length + 1):
            if i == len(rows):
                break
            rows.insert(i, tab_insert)

    rows = [re.sub("REMOVEME123321", "", tab_insert)] + rows

    tab = re.sub(
        ",\nREMOVEME123321", "\n", re.sub("DELETEME123321,", "", ",\n".join(rows))
    )

    return tab


## Helpers to get a token rom Azure's CLI for use in the connection string
class _DataBaseCredentialWrapper:
    def __init__(
        self,
        resource="https://database.windows.net/",
        tenant: str = None,
        tenantid: str = None,
    ):
        self.resource = resource

        if tenantid is None:
            tenantidi = ""
        else:
            tenantidi = "--tenant " + tenantid

        try:
            result = subprocess.check_output("az account show", shell=True)
        except Exception as e:
            result = ""

        if result != "":
            # if (json.loads(result).get('tenantId') != tenantid) and (tenantid is not None):
            #    os.system('az logout')
            az_tenant = re.sub(
                "^.+@|\\.com$", "", json.loads(result).get("user").get("name")
            ).lower()
            if tenant != az_tenant:
                os.system("az logout")

        self.cred = AzureCliCredential()

        try:
            self.cli_token = self.cred.get_token(self.resource)
        except Exception as e:
            if tenant is not None:
                print(
                    "Logging into Azure CLI...\nUse your '{}' credentials.".format(
                        tenant
                    )
                )
            os.system("az login {}".format(tenantidi))
            self.cred = AzureCliCredential()
            self.cli_token = self.cred.get_token(self.resource)


def _prepare_token(token):

    # get bytes from token obtained
    tokenb = bytes(token.cli_token[0], "UTF-8")

    exptoken = b""
    for i in tokenb:
        exptoken += bytes({i})
        exptoken += bytes(1)

    tokenstruct = struct.pack("=i", len(exptoken)) + exptoken
    return tokenstruct
