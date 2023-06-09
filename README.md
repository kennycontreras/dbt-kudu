# dbt-kudu

The `dbt-kudu` adapter allows you to use [dbt](https://www.getdbt.com/) along with [Apache Impala](https://impala.apache.org/) with all the features of Kudu.


## Getting started

- [Install dbt](https://docs.getdbt.com/docs/installation)
- Read the [introduction](https://docs.getdbt.com/docs/introduction/) and [viewpoint](https://docs.getdbt.com/docs/about/viewpoint/)

### Requirements

Current version of dbt-kudu work only with dbt-core 1.3 but not with dbt-core >= 1.4.

Python >= 3.8
dbt-core == 1.3.*

For development/testing or contribution to the dbt-impala, please follow [Contributing](CONTRIBUTING.md) guidelines.

### Installing dbt-kudu

`pip install dbt-kudu`

### Profile Setup

```
demo_project:
  target: dev
  outputs:
    dev:
     type: kudu
     host: impala-coordinator.my.org.com
     port: 443
     schema: my_db
     username: my_user
     password: my_pass
     auth_type: ldap
```

## Supported features
| Name | Supported |
|------|-----------|
|Materialization: Table|Yes|
|Materialization: View|Yes|
|Materialization: Incremental - Append|Yes|
|Materialization: Incremental - Insert+Overwrite|Yes|
|Materialization: Incremental - Merge|No|
|Materialization: Ephemeral|No|
|Seeds|Yes|
|Tests|Yes|
|Snapshots|Yes|
|Documentation|Yes|
|Authentication: LDAP|Yes|
|Authentication: Kerberos|Yes|

### Tests Coverage

#### Functional Tests
| Name | Base |
|------|-----------|
|Materialization: Table|Yes|
|Materialization: View|Yes|
|Materialization: Incremental - Append|Yes|
|Materialization: Incremental - Insert+Overwrite|No|
|Materialization: Incremental - Merge|No|
|Materialization: Ephemeral|No|
|Seeds|Yes|
|Tests|Yes|
|Snapshots|No|
|Documentation|No|
|Authentication: LDAP|No|
|Authentication: Kerberos|No|
