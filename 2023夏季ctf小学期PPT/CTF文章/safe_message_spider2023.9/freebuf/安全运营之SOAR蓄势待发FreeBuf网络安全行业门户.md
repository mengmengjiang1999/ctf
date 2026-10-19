## 前情提要

> [安全运营之SOAR：架构雏形](https://www.freebuf.com/articles/es/256988.html)

## SOAR整体架构

安全编排与自动化响应解决方案（SOAR），主要是通过编排特定的任务，将安全专家的经验以及常规的操作固化，快速得出事件结论并根据预设动作自动化的响应。

在SOAR设计中，任务编排是否灵活、企业IT资源是否适应SOAR，很大程度决定了安全编排的效果。目前主流的SOAR产品主要解决了任务编排的可观性（美观与任务拖拽）及基于PlayBook结果的快速拉动沟通等，在企业设备接口对接方面仍不够完善，当一个很“奇葩”的需求出现，往往很难快速通过一款SOAR产品快速的开发PlayBook去实现需求。

我们的核心需求是一个能让团队成员快速上手编写PlayBook、快速实现安全需求的SOAR架构，于是我们基于开源组件，设计了一套符合自身需求的SOAR。主要由三部分组成（粉红区域），分别是编排引擎、API接口、运营平台。其中
**编排引擎** 选择使用 **airflow** ，承载playbook的周期运行、错误重跑等工作。

本文将主要分享使用 **airflow** 作为安全编排的一部分的实践经验。

![](https://image.3001.net/images/20210114/1610588325_5fffa0a5efe5bb5d8786e.png!small)

## 编排引擎结构

### 体验airflow

当前airflow已经推出2.0.0版本，其架构相对1.x版本有很大的改动，未了解过airflow的读者，建议使用1.x最高的版本1.10.14。

airflow的官方文编写的非常详细，可以参考[1.10.14版本的官方文档](https://airflow.apache.org/docs/apache-airflow/1.10.14/installation.html)进行部署。下文中提到的 **DAG** 与我们编排中所说的
**PlayBook(剧本)** 同义，习惯上，我们将编排任务的python文件称为 **PlayBook** 。

    
    
    # 安装airflow
    pip install apache-airflow
    
    # 安装扩展，选择你需要使用的模块
    pip install apache-airflow[celery,postgres]

安装airflow以后，无需改airflow.cfg配置文件，可通过命令启动airflow。

    
    
    # 初始化数据库，默认情况下使用SQLite
    airflow initdb
    
    # 启动web界面
    airflow webserver -D
    
    airflow scheduler -D

若将airflow部署在生产环境，需要注意配置文件中的几个关键项：

    
    
    # 编写的DAG存放目录
    dags_folder = /airflow/playbooks
    # airflow的日志存放目录
    base_log_folder = /airflow/logs
    # DAG管理进程日志存放目录
    dag_processor_manager_log_location = /airflow/logs/dag_processor_manager/dag_processor_manager.log
    
    # 执行器选择使用celery
    executor = CeleryExecutor
    
    # 数据库连接器
    sql_alchemy_conn = postgresql+psycopg2://username:password@192.168.1.1:5432/airflow
    sql_engine_encoding = utf-8
    
    # 调整DAG运行参数
    parallelism = 32
    dag_concurrency = 16
    max_active_runs_per_dag = 8
    
    # 不加载样例DAG
    load_examples = False
    
    [api]
    # api加上认证
    auth_backend = airflow.contrib.auth.backends.password_auth
    
    [celery]
    celery_app_name = airflow.executors.celery_executor
    worker_concurrency = 16
    worker_log_server_port = 8793
    
    # celery的broker和backend配置
    broker_url = redis://:redis_passwd@192.168.1.1:6379/1
    result_backend = redis://:redis_passwd@192.168.1.1:6379/2
    
    [scheduler]
    # scheduler心跳超时设置
    job_heartbeat_sec = 30
    
    # 设置scheduler清理僵尸任务时间
    scheduler_zombie_task_threshold = 300

### airflow的目录结构

当使用airflow作为任务的编排引擎时，我们知道airflow通过scheduler读取指定目录下的 **python文件**
，最终通过executor执行。那么我们需要设计好存放DAG也就是PlayBook的目录结构，使得我们能快速的、规范的编写我们的PlayBook。

简洁的PlayBook目录结构如下（ **airflow中的配置项：dags_folder = /airflow/soar** ）：

    
    
    soar
    - models # 数据类型
    - ops_pb # 日常运维playbook
    - sec_pb # 安全分析playbook
    - audit_pb # 安全审计playbook
    - tmp_pb # 临时任务playbook
    - utils # 通用工具
    .airflowignore 

**.airflowignore** 的内容（跟.gitignore一样）指定airflow的

