## 0x00 JumpServer与漏洞介绍

JumpServer是一个开源的堡垒机，server端使用python编写开发，开源地址在

> https://github.com/jumpserver/jumpserver。

在上周五被爆出一个 **远程命令执行漏洞** ，这个远程命令执行主要由一个log日志跨目录读取引发。

漏洞影响版本：

> < v2.6.2
>
> < v2.5.4
>
> < v2.4.5
>
> = v1.5.9
>
> >= v.15.3

![1621929464_60acadf891ae60d21e3ac.png!small?1621929465100](https://image.3001.net/images/20210525/1621929464_60acadf891ae60d21e3ac.png!small?1621929465100)

## 0x01 漏洞详情

漏洞主要由两部分组成：

>  **1.跨目录读取log日志来获取token**
>
> 2.利用获取的token构造ws通信payload，在jumpserver所管理的服务器进行命令执行。

本文主要对1部分进行分析，也是漏洞利用的前提关键条件。

log日志读取漏洞触发主要在`apps/ops/ws.py`文件，关键代码为`task_log_f = open(log_path,
'rb')`，位于wait_util_log_path_exist函数。

![1621929490_60acae12d0bdbab26e469.png!small?1621929491121](https://image.3001.net/images/20210525/1621929490_60acae12d0bdbab26e469.png!small?1621929491121)

## 0x02 日志读取漏洞调用链分析

apps/ops/ws.py﻿

的receive函数引入污点

污点由websocket通信进来。查阅相关文档，函数receive中的text_data为用户可控的参数。

![1621929513_60acae2971a6cb7d7eb70.png!small?1621929514057](https://image.3001.net/images/20210525/1621929513_60acae2971a6cb7d7eb70.png!small?1621929514057)

![1621929525_60acae35ebbd53039de9a.png!small?1621929528431](https://image.3001.net/images/20210525/1621929525_60acae35ebbd53039de9a.png!small?1621929528431)

污点传递到handle_task, 又将污点传递给read_log_file

![1621929566_60acae5e45ff7d273a052.png!small?1621929566611](https://image.3001.net/images/20210525/1621929566_60acae5e45ff7d273a052.png!small?1621929566611)

read_log_file函数再传递到上文提及的wait_util_log_path_exist函数![1621929619_60acae93ad30f067e2190.png!small?1621929620449](https://image.3001.net/images/20210525/1621929619_60acae93ad30f067e2190.png!small?1621929620449)

日志读取返回也是在此处，循环读取4096btypes，然后`sleep(0.2)`。

wait_util_log_path_exist
中通过get_celery_task_log_path获取路径，get_celery_task_log_path方法直接将污点拼接到所要读取的日志路径当中，造成一个跨目录的问题![1621929643_60acaeab600489c2ba526.png!small?1621929644067](https://image.3001.net/images/20210525/1621929643_60acaeab600489c2ba526.png!small?1621929644067)

## 0x03 Xcheck自动化审计

xcheck检查结果如下， **仅耗时2s** :

![1621929670_60acaec60650c5aa638a6.png!small?1621929670444](https://image.3001.net/images/20210525/1621929670_60acaec60650c5aa638a6.png!small?1621929670444)

![1621929683_60acaed35d918a2db28e9.png!small?1621929683895](https://image.3001.net/images/20210525/1621929683_60acaed35d918a2db28e9.png!small?1621929683895)

这是我们适配`channels.generic.websocket`之后的检查结果，
**这个适配添加过程仅仅是将`receive`方法的参数设置成污点，剩下的这长长的调用链都可由xcheck自动化完成**。

![1621929704_60acaee8b983ab7709f6b.png!small?1621929705480](https://image.3001.net/images/20210525/1621929704_60acaee8b983ab7709f6b.png!small?1621929705480)

漏洞复现：

本地搭建成功

![1621929730_60acaf02b2ffc71ffe0d4.png!small?1621929731514](https://image.3001.net/images/20210525/1621929730_60acaf02b2ffc71ffe0d4.png!small?1621929731514)

漏洞验证![1621929792_60acaf403a99c9cd024e7.png!small?1621929792917](https://image.3001.net/images/20210525/1621929792_60acaf403a99c9cd024e7.png!small?1621929792917)

实际利用可读取默认log目录`/opt/jumpserver/core/logs`下的日志文件获取token等敏感信息。

漏洞利用进行命令执行的部分本文不进行赘述，可参考《Jumpserver 任意命令执行漏洞分析报告》这篇文章。

## 0x04 参考

>  **修复建议：**
>
>  **《JumpServer 远程命令执行漏洞风险通告，腾讯安全全面检测》**
> https://mp.weixin.qq.com/s/yB7pSlG2ZFz65JDf5A-1Mg
>
> 《Jumpserver 任意命令执行漏洞分析报告》https://mp.weixin.qq.com/s/mJ7nY1r2QWeNzaRK6aZViA

