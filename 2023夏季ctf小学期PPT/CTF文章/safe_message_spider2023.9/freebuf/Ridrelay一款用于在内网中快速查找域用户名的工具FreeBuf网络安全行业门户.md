**今天给大家介绍一款名叫Ridrelay的工具（[@skorov8](https://twitter.com/skorov8)），研究人员可以在只有低等级权限的情况下，利用该工具枚举出内部网络中的域用户名信息。**

![Ridrelay：一款用于在内网中快速查找域用户名的工具](https://image.3001.net/images/20180814/1534221560_5b725cf822e43.png!small)

## RidRelay运行机制

RidRelay整合了SMB Relay攻击技术，常见的基于lsarpc查询和RID循环来获取域用户名列表，其工作步骤如下：

> 1\. 启动一台SMB服务器并等待传入的SMB连接；
>
> 2\. 传入的凭证数据会被中继传输到指定的目标，并创建中继用户的上下文连接；
>
> 3\. 查询请求会传输到SMB连接的lasrpc管道，并获取域用户名信息（通过50000次RID循环实现）；

## 依赖组件

> Python2.7
>
> Impacketv0.9.17（或更新版本）

### 工具安装

    
    
    pipenv install --two
    pipenv shell
     
    #Optional: Run if installing impacket
    git submodule update --init --recursive
    cd submodules/impacket
    python setup.py install
    cd ../..

### 工具使用

首先，找到需要建立中继连接的目标主机，目标主机必须是域成员，而且必须支持SMB，这一步操作可以使用[CrackMapExec](https://github.com/byt3bl33d3r/CrackMapExec)来实现。

运行RidRelay，并指向目标主机：

    
    
    python ridrelay.py -t 10.0.0.50

或者直接将用户名信息输出到文件中：

    
    
    python ridrelay.py -t 10.0.0.50 -o path_to_output.txt

强烈建议：使用Responder来欺骗目标用户连接RidRelay。

### 新版本将添加的功能

> 1\. 添加密码策略枚举功能；
>
> 2\. 寻找拥有管理员权限的凭证，实现动态中继；
>
> 3\. 获取活跃会话连接；
>
> 4\. 整合BloodHound（一款强大的内网域渗透提权分析工具）

 ***
参考来源：[ridrelay](https://github.com/skorov/ridrelay)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

