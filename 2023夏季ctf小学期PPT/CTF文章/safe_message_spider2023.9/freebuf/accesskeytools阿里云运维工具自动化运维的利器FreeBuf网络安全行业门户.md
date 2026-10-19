## 一、简介：

accesskey_tools是一款强大的云计算运维工具，它为云计算环境提供了自动化运维的解决方案。本文将为您介绍accesskey_tools的功能和用途，重点关注其自动创建ECS服务器、批量执行命令以及执行计划任务命令等自动化运维特性。

## 二、优点：

> 在不登录云平台的情况下，通过AccessKey ID和AccessKey Secret 调用API，具有API驱动的高度自定义性。
>
> 批量对服务器ECS实例进行管理和自动化运维操作。批量执行命令及计划任务。
>
> 轻松选择区域，镜像类型，机器配置等信息，去除繁琐的手动操作。

## 三、运维工具使用：

### 1、 安装

    
    
    git clone https://github.com/kohlersbtuh15/accesskey_tools
    cd aliyun
    pip3 install -r requirements.txt

### 2、批量创建ecs实例机器

python3 aliyun_create_ecs.py

根据提示选择机器的各种配置，比如可用区，镜像版本，机器配置，网络等信息。

![](https://image.3001.net/images/20230904/1693829452_64f5c94c4d995d4850751.jpg!small)![](https://image.3001.net/images/20230904/1693829466_64f5c95a104a8e21dc16a.png!small)![](https://image.3001.net/images/20230904/1693829475_64f5c963c40585b61932a.png!small)

可以看到，成功创建2台1h1g的杭州地区ecs实例机器。

### 3、单独执行命令

python3 aliyun_ecs_exec.py

![](https://image.3001.net/images/20230904/1693829495_64f5c977954cffb24dfdf.jpg!small)

### 4、批量执行命令

![](https://image.3001.net/images/20230904/1693829517_64f5c98dd26604617edf6.png!small)![](https://image.3001.net/images/20230904/1693829527_64f5c997721d5d7c5390b.png!small)

### 5、批量执行计划任务

取消aliyun_ecs_exec_batch.py代码中的注释，根据提示选择规则，例如Once立即执行。我此处演示使用的是Period
每5分钟执行一次touch /tmp/5m_test_test.txt：

![](https://image.3001.net/images/20230904/1693829550_64f5c9ae92ac7c8a78172.png!small)![](https://image.3001.net/images/20230904/1693829563_64f5c9bb520250581be60.png!small)![](https://image.3001.net/images/20230904/1693829572_64f5c9c40440fcfd7d9a3.png!small)

## 结论：

本文介绍了accesskey_tools运维工具，并重点强调了其通过API驱动的高度自定义性。利用accesskey_tools的API，您可以轻松选择区域、镜像类型、机器配置等信息，去除繁琐的手动操作，实现更高度的自动化批量和可伸缩性。后续还会继续更新其他云厂商的运维工具(云环境红队利用工具)，大家可以在github提交issue，看到了会回复或者添加需求的功能。

项目地址：[https://github.com/kohlersbtuh15/accesskey_tools](https://link.zhihu.com/?target=https%3A//github.com/kohlersbtuh15/accesskey_tools)

其他文章：<https://www.freebuf.com/sectool/375308.html>

