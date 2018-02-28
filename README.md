# Robot Framework Couchbase Library

Short Description
---

[Robot Framework](http://www.robotframework.org) library to work with Couchbase.

Installation
---

```
pip install robotframework-couchbaselibrary
```

Documentation
---

See keyword documentation for CouchbaseLibrary library on [GitHub](https://github.com/peterservice-rnd/robotframework-cassandracqllibrary/tree/master/docs).

Example
---
```robot
*** Settings ***
Library           CouchbaseLibrary

*** Test Cases ***
View Document In Bucket
    Connect To Couchbase Bucket    my_host_name    8091    bucket_name    password    alias=bucket1
    Connect To Couchbase Bucket    my_host_name    8091    bucket_name    password    alias=bucket2
    Switch Couchbase Bucket Connection    bucket1
    View Document By Key    key=1C1#000
    Switch Couchbase Connection     bucket2
    View Document By Key    key=1C1#000
    Close All Couchbase Bucket Connections
```

License
---

Apache License 2.0

