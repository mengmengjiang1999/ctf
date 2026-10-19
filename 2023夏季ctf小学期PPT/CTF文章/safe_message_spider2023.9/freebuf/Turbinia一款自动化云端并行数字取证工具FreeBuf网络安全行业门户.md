**Turbinia是一款专门用于部署、管理和运行分布式取证任务流的开源框架。该工具可以自动化运行常见的数据取整处理工具，例如Plaso、TSK和strings等等，可帮助研究人员对云端环境以及大量账号下的数字证据进行处理，并尽可能地通过并行处理方式来减少响应时间。  
**

![2.jpg](https://image.3001.net/images/20190328/1553737235_5c9c2613dafe2.jpg!small)  

## 工作机制

Turbinia由客户端、服务器端和业务处理端(Worker)这几种组件组成，这些组件可以在云端环境中运行，也可以在本地运行，或者在这两种混合环境下运行都可以。Turbinia客户端会向Turbinia服务器端发送取证数据的处理请求，服务器端会根据用户发送过来的请求创建逻辑任务，并为Worker创建取证处理计划任务。在允许的情况下，需要处理的取证分析任务会被拆分成多个工作任务，Turbinia会以并行的方式处理这些任务以节省时间开销，服务器端会同时使用一个或多个Worker来持续处理分析任务。任务创建或分配的任何取证数据都将会回传给Turbinia来进行进一步处理。

客户端与服务器端的通信可以由Google Cloud
PubSub或[Kombu](https://github.com/celery/kombu)消息组成。Worker实现和计划任务使用了[PSQ](https://github.com/GoogleCloudPlatform/psq)（Google
Cloud PubSub任务队列）或[Celery](http://www.celeryproject.org/)。

更多关于Turbinia工作机制的内容，可以点击【这里】获取。

## Virtualenv环境下的工具安装

### 创建Virtualenv实例

创建并激活Virtualenv：

    
    
    virtualenv turbinia-env && . turbinia-env/bin/activate

在完成所有操作步骤之前不要退出Virtualenv。

### 构建与配置

安装Turbinia：

    
    
    git clone <https://github.com/google/turbinia.git>
    
    pip install --upgrade pip
    
    pip install -r turbinia/requirements.txt

安装Plaso：

    
    
    curl -o plaso-requirements.txt <https://raw.githubusercontent.com/log2timeline/plaso/master/requirements.txt>
    
    pip install -r plaso-requirements.txt

更新Python路径：

    
    
    cd turbinia; export PYTHONPATH=$PYTHONPATH:`pwd`; cd –
    
    cd turbinia; echo "export PYTHONPATH=$PYTHONPATH" >> ~/.bashrc ;cd -
选择Turbinia配置文件存储路径：

    
    
    /etc/turbinia/turbinia.conf
    
    sudomkdir /etc/turbinia
    
    cp<localgitpath>/turbinia/config/turbinia_config.py/etc/turbinia/turbinia.conf
    
    
    /home/$USER/.turbiniarc
    
    cp<localgitpath>/turbinia/config/turbinia_config.py /home/$USER/.turbiniarc
    
    
    <localgitpath>/turbinia/config/turbinia_config.py

部署云函数：【[传送门](https://github.com/google/turbinia/blob/master/docs/install.md#deploy-the-cloud-functions)】

## 工具使用

工具安装完成后，可以按照下列步骤进行取证处理：

1、 使用下列命令开启Turbinia服务器组件：

    
    
    turbiniactl server 

2、使用下列命令开启一个或多个Turbinia Worker：

    
    
    turbiniactl psqworker

3、 使用下列命令控制Turbinia客户端发送取证任务：

    
    
    turbiniactl ${evidencetype}

4、 使用下列命令检查任务运行状态：

    
    
    turbiniactl status

  
turbiniactl命令可以用来开启不同的组件，下面给出的是基本使用方法：

    
    
    $turbiniactl --help
    
    usage:turbiniactl [-h] [-q] [-v] [-d] [-a] [-f] [-o OUTPUT_DIR] [-L LOG_FILE]
    
                       [-r REQUEST_ID] [-R] [-S][-C] [-V] [-D]
    
                       [-F FILTER_PATTERNS_FILE][-j JOBS_WHITELIST]
    
                       [-J JOBS_BLACKLIST] [-pPOLL_INTERVAL] [-t TASK] [-w]
    
                       <command> ...
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -q, --quiet           Show minimal output
    
      -v, --verbose         Show verbose output
    
      -d, --debug           Show debug output
    
      -a, --all_fields      Show all task status fields in output
    
      -f, --force_evidence  Force evidence processing request inpotentially
    
                            unsafe conditions
    
      -o OUTPUT_DIR, --output_dir OUTPUT_DIR
    
                            Directory path foroutput
    
      -L LOG_FILE, --log_file LOG_FILE
    
                            Log file
    
      -r REQUEST_ID, --request_id REQUEST_ID
    
                            Create new requestswith this Request ID
    
      -R, --run_local       Run completely locally without anyserver or other
    
                            infrastructure. Thiscan be used to run one-off Tasks
    
                            to process data locally.
    
      -S, --server          Run Turbinia Server indefinitely
    
      -C, --use_celery      Pass this flag when using Celery/Kombufor task
    
                            queuing and messaging(instead of Google PSQ/pubsub)
    
      -V, --version         Show the version
    
      -D, --dump_json       Dump JSON output of Turbinia Requestinstead of
    
                            sending it
    
      -F FILTER_PATTERNS_FILE,--filter_patterns_file FILTER_PATTERNS_FILE
    
                            A file containingnewline separated string patterns to
    
                            filter text basedevidence files with (in extended
    
                            grep regex format).This filtered output will be in
    
                            addition to thecomplete output
    
      -j JOBS_WHITELIST, --jobs_whitelistJOBS_WHITELIST
    
                            A whitelist for Jobsthat we will allow to run (note
    
                            that it will not forcethem to run).
    
      -J JOBS_BLACKLIST, --jobs_blacklistJOBS_BLACKLIST
    
                            A blacklist for Jobs we will not allow torun
    
      -p POLL_INTERVAL, --poll_intervalPOLL_INTERVAL
    
                            Number of seconds towait between polling for task
    
                            state info
    
      -t TASK, --task TASK  The name of a single Task to run locally(must be used
    
                            with --run_local.
    
      -w, --wait            Wait to exit until all tasks forthe given request
    
                            have completed
    
     
    
    Commands:
    
      <command>
    
        rawdisk             Process RawDisk as Evidence
    
        googleclouddisk     Process Google Cloud Persistent Disk asEvidence
    
        googleclouddiskembedded
    
                            Process Google CloudPersistent Disk with an embedded
    
                            raw disk image asEvidence
    
        directory          Process a directory asEvidence
    
        listjobs            List all available jobs
    
        psqworker           Run PSQ worker
    
        celeryworker        Run Celery worker
    
        status              Get Turbinia Task status
    
    server              Run Turbinia Server

默认情况下，当添加了新的需要处理的取证任务时，turbiniactl将以客户端的身份向Turbinia服务器发送任务请求，如果没有指定--server参数的话，它将会开启自己的Turbinia服务器进程。下面给出的是turbiniactl添加rawdisk类型任务的示例代码：

    
    
    $./turbiniactl rawdisk -h
    
    usage:turbiniactl rawdisk [-h] -l LOCAL_PATH [-s SOURCE] [-n NAME]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -l LOCAL_PATH, --local_path LOCAL_PATH
    
                            Local path to theevidence
    
      -s SOURCE, --source SOURCE
    
                            Description of thesource of the evidence
    
      -n NAME, --name NAME  Descriptive name of the evidence

### 参考文档

> 1、 [工具安装](https://github.com/google/turbinia/blob/master/docs/install.md)
>
> 2、 [工作机制](https://github.com/google/turbinia/blob/master/docs/how-it-> works.md)
>
> 3、
> [贡献代码](https://github.com/google/turbinia/blob/master/docs/contributing.md)
>
> 4、 [开发新任务](https://github.com/google/turbinia/blob/master/docs/how-it-> works.md)
>
> 5、 [疑难解答](https://github.com/google/turbinia/blob/master/docs/faq.md)
>
> 6、
> [调试常见错误](https://github.com/google/turbinia/blob/master/docs/debugging.md)

 ***
参考来源：[maaaaz](https://github.com/maaaaz/androwarn)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

