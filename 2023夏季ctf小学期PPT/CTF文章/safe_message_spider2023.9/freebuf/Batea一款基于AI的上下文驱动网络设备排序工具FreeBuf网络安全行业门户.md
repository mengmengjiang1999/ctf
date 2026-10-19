![](https://image.3001.net/images/20210210/1612959170_6023cdc2467399d3fc4ef.png!small)

## Batea

Batea是一款基于机器学习算法异常检测分支的上下文驱动的网络设备排序框架，而Batea的主要目标是允许并帮助安全团队使用nmap扫描报告自动过滤大型网络中感兴趣的网络资产。

## Batea工作机制

Batea的工作原理是从nmap报告（XML）中构造所有设备的数字表示（numpy），然后应用异常检测方法来发现感兴趣或有价值的网络资产。我们还可以通过向网络资产元素的数字表示中添加特定的字符来扩展其功能。

网络资产元素的数字表示是使用特征构建的，这些特征受到安全社区专业知识的启发，而无人管理的异常检测方法将允许工具将网络资产上下文或网络的整体描述用作排序算法的核心构建块。这里所使用的准确算法为Isolation
Forest算法。

机器学习模型是Batea的核心。模型是在整个数据集上训练的算法，用于预测相同（和其他）数据点（网络设备）的得分。除此之外，Batea还允许模型持久化。也就是说，我们可以重用预先训练的模型，并导出在大型数据集上训练的模型以供进一步使用。

## 工具安装

    
    
    $ git clone git@github.com:delvelabs/batea.git
    
    $ cd batea
    
    $ python3 setup.py sdist
    
    $ pip3 install -r requirements.txt
    
    $ pip3 install -e .

## 开发者安装

    
    
    $ git clone git@github.com:delvelabs/batea.git
    
    $ cd batea
    
    $ python3 -m venv batea/
    
    $ source batea/bin/activate
    
    $ python3 setup.py sdist
    
    $ pip3 install -r requirements-dev.txt
    
    $ pip3 install -e .
    
    $ pytest

## 工具使用

    
    
    # 完整信息
    
    $ sudo nmap -A 192.168.0.0/16 -oX output.xml
    
     
    
    # 部分信息
    
    $ sudo nmap -O -sV 192.168.0.0/16 -oX output.xml
    
     
    
     
    
    $ batea -v output.xml
    
    工具使用样例
    
    # 简单使用（以默认格式输出排名前五的资产）
    
    $ batea nmap_report.xml
    
    # 输出前三
    
    $ batea -n 3 nmap_report.xml
    
    # 输出所有资产
    
    $ batea -A nmap_report.xml
    
    # 使用多个输入文件
    
    $ batea -A nmap_report1.xml nmap_report2.xml
    
    # 使用通配符
    
    $ batea ./nmap*.xml
    
    $ batea -f csv ./assets*.csv
    
    # 你可以在预训练模型和导出训练模型上使用batea。
    
    # 持久性的训练、输出和转储模型
    
    $ batea -D mymodel.batea nmap_report.xml
    
    # 使用预训练模型
    
    $ batea -L mymodel.batea nmap_report.xml
    
    # 使用预格式化CSV和XML文件
    
    $ batea -x nmap_report.xml -c portscan_data.csv
    
    # Verbose模式
    
    $ batea -vv nmap_report.xml

## 如何添加新的特性

Batea的工作原理是将数字特征分配给报告（或一系列报告）中的每一台主机。这里的主机指的是从nmap报告派生的python对象，它们由以下属性列表组成：[ipv4,
hostname, os_info, ports]，其中的ports是端口对象的列表。每一个端口都有以下属性：[port, protocol, state,
service, software, version, cpe, scripts]，所有属性值默认为None。

Features是从FeatureBase类继承的对象，它实例化了一个特定的_transform方法。这个方法始终将所有主机的列表作为输入，并返回一个lambda函数，该函数将每个主机映射到数值的numpy列（主机顺序是守恒的），然后将该列附加到扫描报告的矩阵表示形式中。Features必须输出正确的数值（浮点或整数），而不能输出其他值。

大多数特征转换都是使用简单的lambda函数实现的，只需确保为每个主机默认一个数值，以实现模型兼容性。

 **具体样例如下：**

    
    
    class CustomInterestingPorts(FeatureBase):
    
        def __init__(self):
    
            super().__init__(name="some_custom_interesting_ports")
    
     
    
        def _transform(self, hosts):
    
          """This method takes a list of hosts and returns a function that counts the number
    
          of host ports member from a predefined list of "interesting" ports, defaulting to 0.
    
     
    
          Parameters
    
          ----------    
          hosts : list
    
              The list of all hosts
    
     
    
          Returns
    
          -------    
          f : lambda function
    
              Counts the number of ports in the defined list.
    
          """
    
            member_ports = [21, 22, 25, 8080, 8081, 1234]
    
            f = lambda host: len([port for port in host.ports if port.port in member_ports])
    
            return f

接下来，我们可以使用batea/__init__.py中的NmapReport.add_feature方法来向报告中添加新的特性：

    
    
    from .features.basic_features import CustomInterestingPorts
    
     
    
    def build_report():
    
        report = NmapReport()
    
        #[...]
    
        report.add_feature(CustomInterestingPorts())
    
     
    
    return report

## 使用预计算表格数据（CSV）

我们还可以使用预处理的数据来训练模型或进行预测。数据必须按（ipv4，port）索引，每行有一个唯一的组合。列必须使用以下名称之一，但不必全部使用。如果缺少列，则解析器默认为空值。

    
    
    'ipv4',
    
      'hostname',
    
      'os_name',
    
      'port',
    
      'state',
    
      'protocol',
    
      'service',
    
      'software_banner',
    
      'version',
    
      'cpe',
    
      'other_info'

 **样例：**

    
    
    ipv4,hostname,os_name,port,state,protocol,service,software_banner
    
    10.251.53.100,internal.delvesecurity.com,Linux,110,open,tcp,rpcbind,"program version   port/proto  service100000  2,3,4        111/tcp  rpcbind100000  2,3,4    "
    
    10.251.53.100,internal.delvesecurity.com,Linux,111,open,tcp,rpcbind,
    
    10.251.53.188,serious.delvesecurity.com,Linux,6000,open,tcp,X11,"X11Probe: CentOS"

## 输出数值表示

我们还可以输出数值矩阵和分数列，而不是常规输出，这对于进一步的数据分析和调试非常有用。

    
    
    $ batea -oM network_matrix nmap_report.xml

## 项目地址

Batea：【[ _GitHub传送门_](https://github.com/delvelabs/batea)】

