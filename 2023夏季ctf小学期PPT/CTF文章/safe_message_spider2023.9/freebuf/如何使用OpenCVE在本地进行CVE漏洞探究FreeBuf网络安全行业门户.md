![](https://image.3001.net/images/20210201/1612170916_6017c6a40c62a5fbde09b.png!small)

## OpenCVE

OpenCVE，之前也被称为Saucs。OpenCVE是一个针对CVE漏洞的研究平台，广大安全研究人员可以在本地搭建该平台，并导入CVE漏洞列表，然后就可以直接在本地搜索关于目标CVE漏洞的详细信息了，比如说相关厂商、产品、CVSS和CWE等等。

用户可以订阅相应的供应商和产品，而OpenCVE可以创建新的CVE或在现有CVE中完成更新时向他们发出警报。

## 工作机制

OpenCVE使用了NVD提供的JSON Feed来更新本地CVE列表。

初始化导入之后，后台任务将会定期执行来同步本地的NVD
Feed拷贝。如果添加了新的CVE，或者检测到了相关的修改，相关厂商或产品的订阅者将会接收到警报提醒。

目前，该平台仅支持通过电子邮件来提醒用户，但将来还会计划整合更多的通知方式。

## 平台要求

OpenCVE的正常运行要求主机安装并配置好Python >= 3.6环境。

为了提升平台性能，OpenCVE使用JSONB功能，因此我们还需要安装一个PostgreSQL实例来存储数据（CVE、用户、厂商、产品和订阅消息等），目前该工具还不支持其他引擎。

该工具使用了Celery来定期获取NVD数据库，并更新CVE列表。因此，我们还需要一个Broker，我们建议大家使用Redis。除此之外，将来OpenCVE可能还会使用缓存功能，而Redis正好可以满足我们的需求。

在向OpenCVE导入初始化数据之后，平台将会下载并解析大量的文件，比如说CPE字典等等。因此，我们建议广大用户的设备至少要有3.5G的RAM。

## 工具安装

广大研究人员可以使用pip命令来安装OpenCVE：

    
    
    $ pip install opencve

## 配置文件

第一步就是创建配置文件，我们需要使用init命令来完成：

    
    
    $ opencve init
    
    [*] Configuration created in /Users/ncrocfer/opencve/opencve.cfg

注意：我们可以在OPENCVE_CONFIG环境变量中指定自定义配置文件的路径。

## 初始化数据库

我们可以使用opencve.cfg文件中的database_uri变量来配置数据库。完成之后，我们就可以使用upgrade-db命令来创建所有的表了：

    
    
    $ opencve upgrade-db

注意：由于OpenCVE使用了JSONB功能来提升平台性能，因此OpenCVE仅支持PostgreSQL数据库。

## 导入数据

数据库创建完成之后，我们需要使用import-data命令来向其导入数据：

    
    
    $ opencve import-data

这个命令可能需要运行几分钟时间，具体取决于厂商和产品的CVE列表，大约要花10分钟。不过别担心，这个操作只需要进行一次。

## 开启Workder

OpenCVE数据库和CVE列表之间的同步操作可以使用一个定时的Celery任务来完成，因此我们必须开启一个Worker和一个计划任务。别忘了，我们还需要在opencve.cfg文件中配置Celery：

    
    
    $ opencve celery worker -l INFO
    
    $ opencve celery beat -l INFO

## 创建一个管理员

    
    
    $ opencve create-user john john.doe@example.com --admin
    
    Password:
    
    Repeat for confirmation:
    
    [*] User john created.

## 开启Web服务器

完成上述所有配置之后，我们就可以开启Web服务器并通过访问地址localhost:8000来使用OpenCVE了：

    
    
    $ opencve webserver
    
    [2020-07-14 20:38:06 +0200] [16032] [INFO] Starting gunicorn 20.0.4
    
    [2020-07-14 20:38:06 +0200] [16032] [INFO] Listening at: http://127.0.0.1:8000 (16032)
    
    [2020-07-14 20:38:06 +0200] [16032] [INFO] Using worker: sync
    
    [2020-07-14 20:38:06 +0200] [16040] [INFO] Booting worker with pid: 16040

注意：服务器名称可以在opencve.cfg文件中的server_name变量中进行自定义配置。

## 平台运行截图

![](https://image.3001.net/images/20210201/1612170972_6017c6dc92215c55d2242.png!small)

![](https://image.3001.net/images/20210201/1612170980_6017c6e4692495eade216.png!small)

![](https://image.3001.net/images/20210201/1612170988_6017c6ec64734aff1c346.png!small)

![](https://image.3001.net/images/20210201/1612170996_6017c6f4756f45243ac22.png!small)

## 项目地址

OpenCVE：【[ _GitHub传送门_](https://github.com/opencve/opencve)】

