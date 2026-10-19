![](https://image.3001.net/images/20201106/1604674647_5fa56457ec7cd22858ac8.png!small)

## DockerENT

DockerENT是一款运行时应用程序安全扫描工具（RAST），该工具基于Python开发，是一个扩展性极强的框架。该工具带有一个命令行接口应用程序和一个简洁的基于[
_StreamLit_](https://www.streamlit.io/)是实现的Web接口。

DockerENT是目前唯一一款能够针对运行时Docker容器和Docker网络进行漏洞分析和错误配置扫描的开源工具。DockerENT旨在检测生产部署中可能导致严重后果的安全性错误配置，它能够与系统中正在运行的容器连接，获取薄弱和易受攻击的运行时配置列表并生成报告。如果通过Web界面调用该工具的话，它将会直接在UI界面中显示扫描和安全审计报告。

## 功能介绍

> 插件驱动式框架；
>
> 使用了低级别Docker API来跟运行时容器进行交互；
>
> 干净简洁、易于使用的UI界面；
>
> 自带九款Docker扫描插件，其中六个支持审计扫描结果【[
> _Docker扫描插件列表_](https://github.com/r0hi7/DockerENT/tree/master/DockerENT/docker_plugins)】；
>
> 支持Docker-Network【[
> _Docker网络扫描插件列表_](https://github.com/r0hi7/DockerENT/tree/master/DockerENT/docker_nw_plugins)】；
>
> 输出插件可以写入文件或HTML；
>
> 开源的交互式Docker扫描工具；
>
> 插件支持并行运行；
>
> 版本更新频繁；

## 工具下载&运行

广大研究人员在本地设备上配置好Python环境之后，即可使用pip来安装DockerENT：

    
    
    pip install DockerENT

接下来，便可以使用下列命令运行DockerENT了：

    
    
    DockerENT -w

没错，就这么简单！

## 运行最新版本

DockerENT的设计是为了保持简单性和可用性，目前您只需克隆存储库并下载依赖项或构建Dockerfile。一旦依赖项已安装在本地系统中，我们就可以运行该工具并分析运行容器的运行时配置。

    
    
    # Download and setup
    
    git clone https://github.com/r0hi7/DockerENT.git
    
    cd DockerENT
    
    make venv
    
    source venv/bin/activate
    
     
    
    # Run
    
    python -m DockerENT --help
    
    usage: Find the vulnerabilities hidden in your running container(s).
    
           [-h] [-d [DOCKER_CONTAINER]] [-p [DOCKER_PLUGINS]]
    
           [-d-nw [DOCKER_NETWORK]] [-p-nw [DOCKER_NW_PLUGINS]] [-w]
    
           [-n [PROCESS_COUNT]] [-a] [-o [OUTPUT]]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -w, --web-app         Run DockerENT in WebApp mode. If this parameter is
    
                            enabled, other command line flags will be ignored.
    
      -n [PROCESS_COUNT], --process [PROCESS_COUNT]
    
                            Run scans in parallel (Process pool count).
    
      -a, --audit           Flag to check weather to audit results or not.
    
     
    
      -d [DOCKER_CONTAINER], --docker [DOCKER_CONTAINER]
    
                            Run scan against the running container.
    
      -p [DOCKER_PLUGINS], --plugins [DOCKER_PLUGINS]
    
                            Run scan with only specified plugins.
    
      -p-nw [DOCKER_NW_PLUGINS], --nw-plugins [DOCKER_NW_PLUGINS]
    
                            Run scan with only specified plugins.
    
     
    
      -d-nw [DOCKER_NETWORK], --docker-network [DOCKER_NETWORK]
    
                            Run scan against running docker-network.
    
     
    
      -o [OUTPUT], --output [OUTPUT]
    
                            Output plugin to write data to.
    
     
    
    # or via the container
    
    docker build . -t dockerent
    
    docker run -d -v /var/run/docker.sock:/var/run/docker.sock -p 8501:8501 --name dockerent dockerent
    
    # Then just open your browser to http://localhost:8051

## 创建自己的插件

如果你想要根据自己的需要来执行运行时扫描，那你可以自行动手创建自己的插件。首先，将下列文件（Demo插件）拷贝到目标路径：

    
    
    cp DockerENT/docker_plugins/docker_sample_plugin.py DockerENT/docker_plugins/docker_demo_plugin.py

接下来，确保文件内的数据结构如下所示：

    
    
    _plugin_name = 'demo_plugin'
    
     
    
    def scan(container, output_queue, audit=False, audit_queue=None):
    
        _log.info('Staring {} Plugin ...'.format(_plugin_name_))
    
     
    
        res = {}
    
     
    
        result = {
    
            'test_class': {
    
                'TEST_NAME': ['good']
    
            }
    
        }
    
     
    
        res[container.short_id] = {
    
            _plugin_name_: result
    
        }
    
        
    
        # Do something magical.
    
     
    
        _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    
     
    
        '''Make Sure you put dict of following structure in Q.
    
        {
    
            'contiainer_id': {
    
                'plugin_name': {
    
                    'test_name_demo1': {
    
                        resultss:[]
    
                    },
    
                    'test_name_demo2': {
    
                        results: []
    
                    }
    
                }
    
            }
    
        }
    
        '''
    
        output_queue.put(res)
    
     
    
        if audit:
    
            _audit(container, res, audit_queue)
    
     
    
    def _audit(container, results, audit_queue):
    
        '''Make Sure to add dict of following structure to Audit Q
    
        res = {
    
            "container_id": [
    
                "_plugin_name_, WARN/INFO/ERROR, details"
    
            ]
    
        }
    
        '''
    
        # Magical logic to perform Audit.
    
    audit_queue.put(res)

接下来，这个插件便会自动加入到工具UI中，非常简单！

## 插件功能

 ** **插件名称****

|

 ** **插件文件****

|

 ** **功能介绍****

|

 ** **审计****  
  
---|---|---|---  
  
CMD_HISTORY

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_cmd_history_info.py)

|

识别Shell历史

|

Root历史和用户Shell历史  
  
FILESYSTEM

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_filesystem_info.py)

|

识别RW文件系统

|

如果RW文件系统存在的话  
  
NETWORK

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_network_info.py)

|

识别网络状态

|

识别所有映射端口  
  
PLAINTEST_PASSWORD

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_plaintext_password_info.py)

|

识别不同文件中的密码

|

无  
  
SECURITY_PROFILES

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_security_profiles_info.py)

|

识别弱安全配置

|

枚举弱安全配置文件  
  
USER_INFO

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_user_info.py)

|

识别用户信息

|

枚举passwd和其他敏感文件中的权限  
  
SYSTEM_INFO

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_system_info.py)

|

识别Docker系统信息

|

无  
  
FILES_INFO

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_file_info.py)

|

识别全局可写入的目录和文件

|

枚举所有此类文件  
  
PROC_INFO

|

[File](https://github.com/r0hi7/DockerENT/blob/master/DockerENT/docker_plugins/docker_process_info.py)

|

识别Docker系统中的进程列表

|

  
  
  
  

## 命令行接口

> 丰富的日志接口，可以通过大量调试日志轻松完成审计调试；
>
> 只需传递-n <count>参数，即可实现并行运行，并指定并行处理器；
>
> 支持JSON和HTML数据导出；

## UI接口

> 干净简洁，易于使用；
>
> 所有数据都显示在一个页面中；
>
> 支持选择多个Docker镜像、多个插件和多个Docker-Networks；
>
> 提供审计报告；

## 工具演示视频

视频地址：【[ _点我观看_](https://asciinema.org/a/Zmtk8KjlbPr1vHa3efZiCIDs2)】

## 项目地址

DockerENT：【[ _GitHub传送门_](https://github.com/r0hi7/DockerENT)】

