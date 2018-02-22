# -*- coding: utf-8 -*-

from couchbase.bucket import Bucket
from couchbase.exceptions import CouchbaseError
from robot.api import logger
from robot.utils import ConnectionCache
from JsonValidator import JsonValidator, JsonValidatorError


class CouchbaseLibrary(object):
    """
    Robot Framework library to work with Couchbase.

    Based on:
    [ http://pythonhosted.org/couchbase | Couchbase Python Client Library]

    == Dependencies ==
    | robot framework | http://robotframework.org |
    | robotframework-jsonvalidator | https://pypi.python.org/pypi/robotframework-jsonvalidator |
    | Couchbase Python Client Library | http://pythonhosted.org/couchbase/ |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        """ Initialization. """
        self._bucket = None
        self._cache = ConnectionCache()

    def connect_to_couchbase_bucket(self, host, port, bucket_name, password=None, alias=None):
        """
        Connect to a Couchbase bucket.

        *Args:*\n
        _host_ - couchbase server host name;\n
        _port_ - couchbase server port number;\n
        _bucket_name_ - couchbase bucket name;\n
        _password_ - password;\n
        _alias_ - connection alias;\n

        *Example:*\n
        | Connect To Couchbase Bucket | my_host_name | 8091 | bucket_name | password | alias=bucket |
        """
        logger.debug('Connecting using : host=%s, port=%s, bucketName=%s, password=%s ' % (host, port, bucket_name,
                                                                                           password))
        connection_string = '{host}:{port}/{bucket}'.format(host=host, port=port, bucket=bucket_name)
        try:
            bucket = Bucket(connection_string, password=password)
            self._bucket = bucket
            return self._cache.register(self._bucket, alias)
        except CouchbaseError as info:
            raise Exception("Could not connect to Couchbase bucket. Error:", str(info))

    def disconnect_from_couchbase_bucket(self):
        """
        Close the current connection with a Couchbase bucket.

        *Example:*\n
        | Connect To Couchbase Bucket | my_host_name | 8091 | bucket_name | password | alias=bucket |
        | Disconnect From Couchbase Bucket |
        """
        if self._bucket:
            self._bucket._close()
        self._cache.empty_cache()

    def close_all_couchbase_bucket_connections(self):
        """
        Close all connections with Couchbase buckets.

        This keyword is used to close all connections in case, there are several open connections.
        Do not use keywords [#Disconnect From Couchbase Bucket | Disconnect From Couchbase Bucket] and
        [#Close All Couchbase Bucket Connections | Close All Couchbase Bucket Connections] together.

        After execution of this keyword, index returned by [#Connect To Couchbase Bucket | Connect To Couchbase Bucket]
        starts at 1.

        *Example:*\n
        | Connect To Couchbase Bucket | my_host_name | 8091 | bucket_name | password | alias=bucket |
        | Close All Couchbase Bucket Connections |
        """
        self._bucket = self._cache.close_all()

    def switch_couchbase_bucket_connections(self, index_or_alias):
        """
        Switch between active connections with Couchbase buckets using their index or alias.

        Connection alias is set in [#Connect To Couchbase Bucket | Connect To Couchbase Bucket],
        which also returns the connection index.

        *Args:*\n
        _index_or_alias_ - connection index or alias;

        *Returns:*\n
        Index of the previous connection.

        *Example:*\n
        | Connect To Couchbase Bucket | my_host_name | 8091 | bucket_name | password | alias=bucket1 |
        | Connect To Couchbase Bucket | my_host_name | 8091 | bucket_name | password | alias=bucket2 |
        | Switch Couchbase Bucket Connection | bucket1 |
        | View Document By Key | key=1C1#000 |
        | Switch Couchbase Connection | bucket2 |
        | View Document By Key | key=1C1#000 |
        | Close All Couchbase Bucket Connections |
        """
        old_index = self._cache.current_index
        self._bucket = self._cache.switch(index_or_alias)
        return old_index

    def view_document_by_key(self, key):
        """
        Get information about the presence of a document in the Couchbase bucket by the given key.
        Depending on the value of the return code, the presence or absence of the document in the bucket is determined.

        *Args:*\n
        _key_ - document key;\n

        *Returns:*\n
        Value of return code.\n
        If rc=0, the document is available in the bucket.

        *Example:*\n
        | ${rc}= | View Document By Key | key=1C1#000 |
        """
        result = self._bucket.get(key, quiet=True).rc
        return result

    def bucket_contains_document_by_key(self, key):
        """
        Check if the Couchbase bucket contains the document by the given key.
        Also it's possible to specify a reference document for comparison.
        The option `quite` is used to check the presence of the document in the bucket.

        *Args:*\n
        _key_ - document key;\n

        *Returns:*\n
        True, if there is a document with this key.

        *Example:*\n
        | ${contain}=   |   Bucket Contains Document By Key |   key=1C1#000 |
        | Should Be True    |   ${contain}  |
        """
        result = self._bucket.get(key, quiet=True)
        logger.debug("{key} contains is {success} with code={code}".format(key=key, success=result.success,
                                                                           code=result.rc))
        return result.success is True

    def get_document_cas_by_key(self, key):
        """
        Get CAS of the document in the Couchbase bucket by the given key.

        *Args:*\n
        _key_ - document key;\n

        *Returns:*\n
        CAS value of the document.\n

        *Example:*\n
        | ${cas}= | Get Document Cas By Key | key=1C1#000 |
        """
        result = self._bucket.get(key).cas
        return result

    def get_document_value_by_key(self, key):
        """
        Get a document value in the Couchbase bucket by the given key.

        *Args:*\n
        _key_ - document key;\n

        *Returns:*\n
        Dictionary with the value of the document.\n

        *Example:*\n
        | ${value}= | Get Document Value By Key | key=1C1#000 |
        """
        result = self._bucket.get(key).value
        return result

    def validate_document_by_json(self, key, json_expr):
        """
        Checking a document to match the json expression.
        The document is specified by the key in the bucket.

        *Args:*\n
        _key_ - document key in the bucket;\n
        _json_expr_ - JSONSelect expression.\n

        *Returns:*\n
        True if the document exists in the bucket and matches the json expression.\n

        *Example:*\n
        | ${valid}= |   Validate Document By Json   |   key=dockey  |   json_expr=.somekey:val("value") |
        | Should Be True    |   ${valid}  |
        """
        result = self._bucket.get(key, quiet=True)
        if result.success is not True:
            return False
        try:
            validator = JsonValidator()
            json_txt = validator.json_to_string(result.value)
            validator.element_should_exist(json_txt, json_expr)
        except JsonValidatorError as error:
            logger.debug("on json validation got exception {ex}".format(ex=error))
            return False
        return True

    def certainly_delete_document_by_key(self, key):
        """
        Remove a document for a given key from Couchbase bucket.
        Doesn't raise NotFoundError if the key doesn't exist.

        *Args:*\n
        _key_ - document key;\n

        *Example:*\n
        | Certainly Delete Document By Key | key=1C1#000 |
        """
        self._bucket.remove(key, quiet=True)

    def upsert_document(self, key, value):
        """
        Insert or update a document in the current Couchbase bucket.

        *Args:*\n
        _key_ - document key;\n
        _value_ - document body;\n

        *Example:*\n
        |   Upsert Document |   somekey |   {'key': 'value'}    |
        """
        self._bucket.upsert(key, value)
