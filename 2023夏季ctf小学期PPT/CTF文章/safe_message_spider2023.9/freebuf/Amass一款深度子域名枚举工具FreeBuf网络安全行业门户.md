![1.png](https://image.3001.net/images/20180703/15306117203663.png!small)**今天给大家介绍的是一款名叫Amass的深度子域名枚举工具，该工具采用Go语言开发，它可以通过遍历等形式爬取数据源和Web文档，或利用IP地址来搜索相关的网块和ASN，并利用所有收集到的信息来构建目标网络拓扑。**

## ![2.png](https://image.3001.net/images/20180703/15306117283097.png!small)
如何安装

### 预编译

获取Amass的预编译版本：【[点我获取](https://github.com/caffix/amass/releases)】

如果你的操作系统环境支持[Snap](https://docs.snapcraft.io/core/install)，你可以点击【[这里](https://snapcraft.io/amass)】或在命令行中使用下列命令完成安装：

    
    
    $sudo snap install amass

如果你想使用snap来获取amass的最新版本（非稳定版），你可以输入下列命令：

    
    
    $sudo snap install --edge amass

### 获取源码

如果你想自己构建最新版本源码，请确保你的设备配置好了Go >= 1.10的开发环境，更多信息请参考Golang官网。

1\. 下载[amass](https://github.com/caffix/amass/releases)：

    
    
    $ goget -u github.com/caffix/amass

2\. 字典文件路径如下：

    
    
    $ ls $GOPATH/src/github.com/caffix/amass/wordlists/

## 工具使用

以下命令可以进行反向DNS查询和名称变更：

    
    
    $amass -d example.com

如果你只需要amass使用被动数据源并且不对域名进行解析的话，使用下列命令：

    
    
    $amass -nodns -d example.com

下面给出的是amass的常用样例：

    
    
    $amass -v -ip -brute -min-for-recursive 3 -d example.com
    [Google]www.example.com
    [VirusTotal]ns.example.com
    ...
    13139names discovered - archive: 171, cert: 2671, scrape: 6290, brute: 991, dns:250, alt: 2766  
    

添加需要枚举的额外域名：

    
    
    $amass -d example1.com,example2.com -d example3.com

下面命令可让amass发送所有的DNS和基础设施枚举数据到Neo4j高性能图形数据库：

    
    
    $amass -neo4j neo4j:DoNotUseThisPassword@localhost:7687 -d example.com

### 网络/基础设施选项

注意：如果你使用下列选项，amass将会尝试访问目标基础设施中所有的IP地址，并从TLS证书中获取更多信息。下面给出的所有选项都需要指定“net”子参数。

搜索目标ASN托管的所有域名：

    
    
    $amass net -asn 13374,14618

查询目标CIDR：

    
    
    $amass net -cidr 192.184.113.0/24,104.154.0.0/15

指定IP地址范围：

    
    
    $amass net -addr 192.168.1.44,192.168.2.1-64

默认配置下，443端口是默认的证书检测端口，但可以使用下列命令修改：

    
    
    $amass net -cidr 192.168.1.0/24 -p 80,443,8080

### 整合Amass代码

如果你想在自己的Go代码中使用amass数据包，请确保设置好了正确的伪随机数生成器：

    
    
    import(
    
        "fmt"
    
        "math/rand"
    
        "time"
    
     
    
        "github.com/caffix/amass/amass"
    
    )
    
     
    
    funcmain() {
    
        output := make(chan *amass.AmassOutput)
    
     
    
        go func() {
    
            for result := range output {
    
                fmt.Println(result.Name)
    
            }
    
        }()
    
     
    
        // Seed the default pseudo-random numbergenerator
    
        rand.Seed(time.Now().UTC().UnixNano())
    
     
    
        // Setup the most basic amass configuration
    
        config :=amass.CustomConfig(&amass.AmassConfig{Output: output})
    
       config.AddDomains([]string{"example.com"})
    
     
    
        // Begin the enumeration process
    
        amass.StartEnumeration(config)
    
    }

## 设置Amass和Maltego  

![3.png](https://image.3001.net/images/20180703/15306118597663.png!small)![4.png](https://image.3001.net/images/20180703/15306118593282.png!small)

![5.png](https://image.3001.net/images/20180703/15306118597538.png!small)

 ***
参考来源：[amass](https://github.com/caffix/amass)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

