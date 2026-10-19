**今天给大家介绍的是一款名叫Beagle的开源工具，Beagle是一款事件响应与数字取证工具，它可以将安全日志与分析数据以图形化的形式呈现。**

![1.png](https://image.3001.net/images/20190429/1556516613_5cc68f052ff52.png!small)  

## Beagle介绍

Beagle是一款功能强大的图形化事件响应与数字取证安全分析工具，支持FireEye HX Triages、Windows
EVTX文件、SysMon日志以及Windows内存源镜像等多种数据源。导出的图形化分析结果可以发送至类似Neo4J和DGraph这样的图形化数据库，或者直接以Python
NetworkX对象存储在本地。

Beagle能够以Python库的形式使用，或者直接在Web接口中调用：

![2.png](https://image.3001.net/images/20190429/1556516630_5cc68f16a59c2.png!small)  

库可以直接通过函数调用序列来调用：

    
    
    >>>from beagle.datasources import SysmonEVTX
    
     
    
    >>>graph = SysmonEVTX("malicious.evtx").to_graph()
    
    >>>graph
    
    <networkx.classes.multidigraph.MultiDiGraphat 0x12700ee10>

或严格按照图形处理过程中调用数据源的每一个分析步骤来进行调用：

    
    
    >>>from beagle.backends import NetworkX
    
    >>>from beagle.datasources import SysmonEVTX
    
    >>>from beagle.transformers import SysmonTransformer
    
     
    
    >>>datasource = SysmonEVTX("malicious.evtx")
    
     
    
    #Transformers take a datasource, and transform each event
    
    #into a tuple of one or more nodes.
    
    >>>transformer = SysmonTransformer(datasource=datasource)
    
    >>>nodes = transformer.run()
    
     
    
    #Transformers output an array of nodes.
    
    [
    
        (<SysMonProc>process_guid="{0ad3e319-0c16-59c8-0000-0010d47d0000}"),
    
        (<File>host="DESKTOP-2C3IQHO"full_path="C:\Windows\System32\services.exe"),
    
        ...
    
    ]
    
     
    
    #Backends take the nodes, and transform them into graphs
    
    >>>backend = NetworkX(nodes=nodes)
    
    >>>G = backend.graph()
    
    <networkx.classes.multidigraph.MultiDiGraphat 0x126b887f0>

图形化输出位于每一个分析进程的中间位置，可以帮助研究人员快速了解目标主机中的详细状态。

## 工具安装

### Docker

Beagle能够直接以Docker文件来安装使用：

    
    
    docker pull yampelo/beagle
    
    mkdir -p data/beagle
    
    docker run -v "$PWD/data/beagle":"/data/beagle" -p 8000:8000yampelo/beagle

### Python包

Beagle还能够以Python库的形式使用。完整的API文档：【[传送门](https://beagle-graphs.readthedocs.io/)】

    
    
    pip install pybeagle

注意：目前Beagle仅支持Python 3.6+。

安装完成后，使用下列命令安装Rekall：

    
    
    pip install pybeagle[rekall]

## 工具配置

配置文件中的每一个参数都可以通过环境变量来设置和修改，格式如下：

    
    
    BEAGLE__{SECTION}__{KEY}

比如说，你想在使用Docker镜像的时候修改VirusTotal API密钥，你就可以使用-e参数并设置BEAGLE__VIRUSTOTAL__API_KEY变量：

    
    
    dockerrun -v "data/beagle":"/data/beagle" -p 8000:8000 -e"BEAGLE__VIRUSTOTAL__API_KEY=$API_KEY" beagle

环境变量和目录可以使用Docker组件来定义：

    
    
    version:"3"
    
     
    
    services:
    
        beagle:
    
            image: yampelo/beagle
    
            volumes:
    
                - /data/beagle:/data/beagle
    
            ports:
    
                - "8000:8000"
    
            environment:
    
                - BEAGLE__VIRUSTOTAL__API_KEY=$key$

## Web接口

Beagle的Docker镜像还封装了Web接口，可以帮助我们将数据以图形化的形式呈现，或将图形化数据以文本数据呈现。

上传数据：

![3.png](https://image.3001.net/images/20190429/1556516753_5cc68f91ed8c8.png!small)  

浏览图形化数据：

![4.png](https://image.3001.net/images/20190429/1556516762_5cc68f9ad0075.png!small)  

图形接口：

![5.png](https://image.3001.net/images/20190429/1556516771_5cc68fa3ae6df.png!small)  

数据节点：

![6.png](https://image.3001.net/images/20190429/1556516779_5cc68fabe4a9b.png!small)  

数据连线：

![7.png](https://image.3001.net/images/20190429/1556516788_5cc68fb4d4561.png!small)  

## Python库

我们可以根据自己的需要来使用Python库生成图形化数据，图形数据生成由下列三个步骤组成：

1、 DataSource类负责对事件进行单独解析；

2、 Transformer类负责接收输入数据，并将其转换为Node类；

3、 Backend类负责接收节点数组，并将其存入图形结构的特定位置；

Python包可以通过pip安装：

    
    
    pip install pybeagle

创建图形化数据需要使用to_graph()函数：

    
    
    from beagle.datasources import HXTriage
    
     
    
    # Bydefault, using the to_graph() class uses NetworkX and the first transformer.
    
    G =HXTriage('test.mans').to_graph()
    
    <networkx.classes.multidigraph.MultiDiGraphat 0x12700ee10>

你可以定义需要使用的Backend，并将数据发送至DGraph：

    
    
    from beagle.datasources import HXTriage
    
    from beagle.backends import DGraph
    
    from beagle.transformers import FireEyeHXTransformer
    
     
    
    # Thedata will be sent to the DGraph instance configured in the
    
    #configuration file
    
    backend= HXTriage('test.mans').to_graph(backend=DGraph)
    
     
    
    # Canalso specify the transformer
    
    backend= HXTriage('test.mans').to_transformer(transformer=FireEyeHXTransformer).to_graph(backend=DGraph)

在调用to_graph或to_transformer方法时，你可以向这些类传递任何参数：

    
    
    from beagle.datasources import HXTriage
    
    from beagle.backends import Graphistry
    
     
    
    #Send the graphistry, anonymize the data first, and return the URL
    
    graphistry_url= HXTriage('test.mans').to_graph(backend=Graphistry, anonymize=True,render=False)

你还可以手动完成上述步骤：

    
    
    >>>from beagle.backends import NetworkX
    
    >>>from beagle.datasources import HXTriage
    
    >>>from beagle.transformers import FireEyeHXTransformer
    
     
    
    >>>datasource = HXTriage("test.mans")
    
    >>>transformer = FireEyeHXTransformer(datasource=datasource)
    
    >>>nodes = transformer.run()
    
    >>>backend = NetworkX(nodes=nodes)
    
    >>>G = backend.graph()

## 项目地址

Beagle：【[GitHub传送门](https://github.com/yampelo/beagle)】

### 参考资料

> 1、 <https://github.com/yampelo/beagle/blob/master/docs/rest_api.md>
>
> 2、 <https://github.com/yampelo/beagle/blob/master/docs/configuration.md>
>
> 3、 <https://github.com/yampelo/beagle/blob/master/docs/development.md>
>
> 4、 <https://github.com/yampelo/beagle/blob/master/docs/design_overview.md>

***参考来源：[beagle](https://github.com/yampelo/beagle)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

