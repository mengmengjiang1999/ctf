![a.png](https://image.3001.net/images/20190405/1554452820_5ca71154245f0.png!small)

**今天给大家介绍的是一款名叫Arjun的开源工具，广大研究人员可以利用该工具来对HTTP参数进行提取和分析。**

![b.png](https://image.3001.net/images/20190405/1554452824_5ca71158ebeb1.png!small)

## 功能介绍

> 1、 多线程；
>
> 2、 四种检测模式；
>
> 3、 常规扫描仅需30秒；
>
> 4、 基于正则表达式的启发式扫描；
>
> 5、 提供了25980个可扫描的参数名；
>
> 6、 只想目标发送30-5个请求即可完成任务；

## 工具使用

注意：当前版本的Arjun不支持Python < 3.4的环境。

### 参数发现

用户可以使用下列命令查找GET参数：

    
    
    python3 arjun.py -u https://api.example.com/endpoint --get
    

类似的，用户可以使用--post来查找POST请求。

### 多线程

Arjun默认仅会使用两个线程，广大用户可以根据自己的网络连接状况或特定需求来调整Arjun性能：

    
    
    python3 arjun.py -u https://api.example.com/endpoint --get -t 22
    

### 请求间隔延迟

用户可以使用-d选项来延迟请求发送的间隔时间：

    
    
    python3 arjun.py -u https://api.example.com/endpoint --get -d 2
    

### 引入固定数据

比如说你设置了一个API密钥，并且每次发送请求时都需要携带这个密钥，那你就可以使用--include参数来告知Arjun：

    
    
    python3 arjun.py -u https://api.example.com/endpoint --get --include 'api_key=xxxxx'
    

或者：

    
    
    python3 arjun.py -u https://api.example.com/endpoint --get --include'{"api_key":"xxxxx"}'
    

如果你需要传入多个参数的话，你可以使用“&”来分隔不同参数，或以有效的JSON对象格式进行传递。

### JSON输出

用户可以使用-o参数来以JSON格式存储工具的输出结果：

    
    
    python3 arjun.py -u https://api.example.com/endpoint --get -o result.json
    

## 添加HTTP Header

用户可以使用“--headers”选项来开启交互式命令行，然后输入需要设置的header。完成之后，按下Ctrl + S键保存配置，然后按下Ctrl +
X进行数据处理。

![c.png](https://image.3001.net/images/20190405/1554452891_5ca7119baba18.png!small)

***参考来源：[Arjun](https://github.com/s0md3v/Arjun/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

