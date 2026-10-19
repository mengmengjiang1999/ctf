## 前言

 **DFIRTrack(Digital Forensics and Incident Response Tracking
application)，即数字取证和事件响应跟踪应用程序。它是一款开源的Web应用程序，基于[Django](https://www.djangoproject.com/)开发，后端数据库为[PostgreSQL](https://www.postgresql.org/)数据库。**

DFIRTrack专注于处理一个重大安全事件，其中需要涉及到多个受影响的系统，这也符合很多APT攻击事件的特性。在大型网络攻击事件场景下，它可以被用作专门的事件响应工具。当然了，CERT和SOC也可以使用DFIRTrack，不过它只能在特殊情况下使用，并不适用于日常响应工作。

## 功能介绍

DFIRTrack跟其他基于事件案例的应用程序不同，它以基于系统的方式运行，它能够跟踪各种系统的状态以及相关的任务，来帮助分析人员在事件的调查阶段以及响应阶段了解受影响系统的状态和数量。

![](https://image.3001.net/images/20190215/1550214817_5c6666a1ea75a.png!small)

它的主要功能之一就是快速导出受影响系统的相关信息，并给技术人员以电子表格的形式提供详细的安全报告，而且数据集中不存在任何冗余数据或偏差。

### 目前该工具支持以下功能：

 **1、 导入器**

> a) 系统及任务创建工具（通过Web接口快速创建多个相关实例）
>
> b) CSV（基于CSV生成和导入，解和主机名、IP及Web表单）
>
> c) 标记实体

 **2、 导出器**

> a) 标注系统报告（MkDocs结构）
>
> b) 电子表格（CSV和XLS）
>
> c) LaTeX

## 工具安装及依赖组件

DFIRTrack支持Debian Stretch或Ubuntu 16.04，其他Debian发行版理论上同样支持，但未进行过测试。

工具的编译安装，请参考Ansible
Playbook：【[传送门](https://github.com/stuhli/dfirtrack_ansible)】

该工具至少需要以下依赖组件：

    
    
    django(2.0),
    
    django_q,
    
    djangorestframework,
    
    gunicorn,
    
    postgresql,
    
    psycopg2-binary,
    
    python3-pip,
    
    PyYAML,
    
    requests,
    
    virtualenv,
    
    xlwt.

请注意，代码库中没有提供settings.py，大家可以点击【[这里](https://github.com/stuhli/dfirtrack_ansible/blob/master/roles/dfirtrack/templates/settings.py.j2)】获取。

## Docker环境

项目提供了仅支持本地使用的Docker实验环境，在项目主目录下运行下列命令即可开启环境：

    
    
    docker-compose up

工具已创建好了管理员用户，大家可以编辑下列文件来修改密码：

    
    
    docker/setup_admin.sh

应用程序访问地址为：[localhost:8000](http://localhost:8000/)。

## 内置软件

DFIRTrack实现了以下项目或代码库：

[](https://github.com/twbs/bootstrap)

> [clipboard.js](https://github.com/zenorocha/clipboard.js)
>
> [DataTables](https://github.com/DataTables/DataTables)
>
> [jQuery](https://github.com/jquery/jquery)
>
> [Open Iconic](https://github.com/iconic/open-iconic)
>
> [Popper.js](https://github.com/FezVrasta/popper.js)

## 项目地址

DFIRTrack：【[传送门](https://github.com/stuhli/dfirtrack)】

 ***参考来源：[kitploit](https://www.kitploit.com/2019/02/dfirtrack-incident-response-tracking.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

