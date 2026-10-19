## 一、 关于accesskey_tools

"accesskey-Tools" 是一个基于 Python
开发的多平台云环境利用辅助脚本。该工具可用于渗透测试中，因开发的不规范，以及一些其它漏洞，拿到泄漏AK/SK的情况下，测试人员可以直接利用这些凭证对云服务器进行测试，及时修复风险并采取相应措施，确保云环境中的敏感凭证不会被滥用或泄露。

当前已支持的云：

  * 阿里云

  1. ECS 查询阿里云各地区的ecs实例的详情信息，指定实例可执行系统命令。
  2. RDS 查询阿里云所有rds详情信息，以及IP白名单限制信息。
  3. OSS 查询所有bucket存储桶信息，可指定bucket以及bucket的文件夹。

  * 腾讯云

  1. CVM 查询腾讯云各地区的cvm实例的详情信息，指定实例可执行系统命令。
  2. COS 查询所有bucket存储桶信息，可指定bucket以及bucket的文件夹。

todolist：

  * AWS
  * 华为云
  * 七牛云
  * ......

优点：  
1、适用于多云平台使用，在不登录云平台的情况下，通过AccessKey ID和AccessKey Secret
调用API完成对服务器ECS实例的管理和自动化运维操作。

2、简单易用，快速上手，可配置socks5代理，可自定义资源扫描区域。

3、采用多线程+消息队列，下载速度更快。

## 二、工具下载

    
    
    git clone https://github.com/kohlersbtuh15/accesskey_tools.git
    

## 三、安装依赖

    
    
    cd aliyun/tencentcloud #进入相应的云服务平台
    pip3 install -r requirements.txt
    

## 四、配置config

Config中对Access Key ID和AccessKeySecret进行配置访问凭证。

SOCKS5_PROXY_HOST和SOCKS5_PROXY_PORT可设置socks5代理。

RegionIds用于自定义扫描的地区。

![](https://image.3001.net/images/20230817/1692272655_64de080fb043d091afd51.png!small)

默认不开启代理，如需使用，配置完config之后，在各个功能代码中取消如下注释。

![](https://image.3001.net/images/20230817/1692272674_64de0822e1234a2a7b4d2.png!small)

## 五、快速上手

### 1、ECS执行命令

配置好config.py之后运行脚本。

会先对各地区进行扫描机器实例，然后输出实例信息。

![](https://image.3001.net/images/20230817/1692272710_64de0846d8f2f7729673a.png!small)

输入InstanceId，指定命令类型

0:SHELL即为linux shell命令 ；

1:POWERSHELL即为Windows Powershell命令。

![](https://image.3001.net/images/20230817/1692272733_64de085d3e6103d7f2c45.png!small)

### 2、COS下载文件

运行脚本会先列出当前accesskey下的所有bucket。

![](https://image.3001.net/images/20230817/1692272761_64de087942da19d4db8b5.png!small)

all模式下载所有bucket的文件。

![](https://image.3001.net/images/20230817/1692272784_64de089089ef3ea254056.png!small)

指定bucketname会下载对应bucket中的文件，在当前目录按照bucket名字进行生成文件夹。

![](https://image.3001.net/images/20230817/1692272797_64de089d7bfc9366ff8ad.png!small)

### 3、RDS查询实例信息和IP白名单

显示实例id，数据库类型版本，IP白名单等信息。

![](https://image.3001.net/images/20230817/1692272820_64de08b493d3424400867.png!small)

## 六、后续更新

后续会更新其他云平台的accesskey自动运维工具，以及扩充其他功能，敬请期待。有其他关于功能上的建议也可以在github提交issus。

