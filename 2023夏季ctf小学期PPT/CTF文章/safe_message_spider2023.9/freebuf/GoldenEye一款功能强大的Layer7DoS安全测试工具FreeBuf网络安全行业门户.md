**PS：本文仅作为技术分享，禁止用于其他非法用途**

 **今天给大家介绍一款名叫GoldenEye的安全测试工具，广大研究人员可利用该工具来对目标系统进行DoS攻击测试。**

![1111.png](https://image.3001.net/images/20180829/1535516306_5b861e92d55d3.png!small)

## 工具介绍

GoldenEye是一款Layer 7拒绝服务测试工具，采用Python语言开发。这是一款HTTP DoS测试工具，可帮助研究人员对目标项目进行安全测试。

利用的攻击向量：HTTP Keep Alive + NoCache

### 工具使用

  
![2222.png](https://image.3001.net/images/20180829/1535516336_5b861eb0965e1.png!small)

### 参数介绍

> -u：指定需要使用的user-agent列表文件（默认随机生成）；
>
> -w：指定并行worker数量（默认50）；
>
> -s：指定并行socket数量（默认30）；
>
> -m：指定使用的HTTP方法，“get“、”post“或”random“（默认get）；
>
> -d：启用调试模式，可输出更多的verbose内容（默认False）；
>
> -n：关闭SSL证书验证功能（默认True）；
>
> -h：查看帮助信息

## 实用组件

> 1\.
> util/getuas.py：利用<http://www.useragentstring.com/pages/useragentstring.php>获取user-> agent列表；
>
> 2\. res/lists/useragents：User-> Agent字符串列表，文本格式，每条记录一行（获取源：<http://www.useragentstring.com/>）

## 使用样例

获取User-Agent列表（依赖组件：BEAUTIFULSOUP4）：

    
    
    ./getuas.py http://www.useragentstring.com/pages/Browserlist/

## 修改日志

2016-02-06：增加SSL证书验证功能；

2014-02-20：增加user-agent随机创建功能；

2014-02-19：移除无效referer和user-agent，提升referer随机性，增加外部user-agent列表支持；

2013-03-26：增加多线程支持，但目前仍然有bug需要修复；

2012-12-09：项目发布；

## 许可证

本项目遵循GPLv3许可证协议。

 ***
参考来源：[GoldenEye](https://github.com/jseidl/GoldenEye)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

