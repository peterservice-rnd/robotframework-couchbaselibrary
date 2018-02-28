Robot Framework Couchbase Library
=================================

|Build Status|

Short Description
-----------------

`Robot Framework`_ library to work with Couchbase.

Installation
------------

::

    pip install robotframework-couchbaselibrary

Documentation
-------------

See keyword documentation for CouchbaseLibrary library on `GitHub`_.

Example
-------

.. code:: robot

    *** Settings ***
    Library           CouchbaseLibrary
    Test Setup        Connect To Couchbase
    Test Teardown     Close All Couchbase Bucket Connections

    *** Test Cases ***
    View Document In Bucket
        Switch Couchbase Bucket Connection    bucket1
        View Document By Key    key=1C1#000
        Switch Couchbase Connection     bucket2
        View Document By Key    key=1C1#000

    *** Keywords ***
    Connect To Couchbase
        Connect To Couchbase Bucket    my_host_name    8091    bucket_name    password    alias=bucket1
        Connect To Couchbase Bucket    my_host_name    8091    bucket_name    password    alias=bucket2

License
-------

Apache License 2.0

.. _Robot Framework: http://www.robotframework.org
.. _GitHub: https://github.com/peterservice-rnd/robotframework-cassandracqllibrary/tree/master/docs

.. |Build Status| image:: https://travis-ci.org/peterservice-rnd/robotframework-couchbaselibrary.svg?branch=master
   :target: https://travis-ci.org/peterservice-rnd/robotframework-couchbaselibrary