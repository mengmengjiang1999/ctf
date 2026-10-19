## 呦~大家好

之前我在Secquan社区公众号上看到这样一篇文章，感觉还不错就放在收藏夹里，直到现在才拿出来看看到底能不能实现批量挖漏洞，让它解放我的双手。  
我个人感觉这两个工具联合起来是能挖到漏洞，但是效率一般般，就当学习记录分享给大家  
首先说一下：  
涉及的工具：fofa、xray。  
这两个工具如果进一步了解的话，可以上百度查，咱学院的SSG老师也写过Xray的文章可以去看看

## 0x00工具介绍

这个两个工具联动叫fofa2xray，用Golang语言编写的。windows、linux都能用

## 0x01工具原理

简单来说用fofa的api把查询到的内容保存下来，xray主动去进行漏洞检测，其次把有效漏洞记录在相对于的文件夹中。

## 0x02工具搭建使用

工具是在Github上下载的，由于有些时候在Github上下载的异常缓慢，所以我把我下载的工具放在附件里提供大家下载，要注意区分windows和linux的文件名压缩包喔  
下载解压之后是这样的  
![](https://image.3001.net/images/20210201/1612156779_60178f6b8ca0216f5777e.png!small)

### 更改配置文件———f2Xconfig.yaml

 **就更改这一个配置文件就可以了**

fofa:  
email: {fofa账户}  
key: {fofaKey}

###### #这个是fofa的邮箱和key，这些都在fofa的个人资料里都能看见

###### # 固定查询语句

fixedQuerySyntexList:  
status_code=200  
country=”CN”

###### # 查询语法

###### # 更多查询语法见<https://fofa.so/>

querySyntax: host

###### # 使用querySyntax查询语法分别查询target

targetList:  
一 .edu.cn  
xray:

###### #这个路径是fofa2Xray下xray的绝对路径

path: D:\CyberSecurityTools\xray_windows_amd64\xray_windows_amd64.exe

###### #fofa2Xray相同目录下xray的全名，默认不用更改这里

name: xray_windows_amd64.exe

###### #同时运行xray的最大数

### thread: 10

##### 关于配置文件的最后说明

1、到这里这个配置文件就基本改完了，但是这里要特别说明，配置文件fofa那里的邮箱和key记得把{}删掉，不要掉坑里了。  
2、对于fofa2Xray他可以指定对.edu.cn或者.com这样的域名来爬取扫描漏洞，这个脚本默认是对.edu.cn来进行漏扫的，默认的规则组合起来就是文件的名字，可以自行更改，组合起来的规则语句就是自动生成文件的那个文件名。

#### 演示

我在这里就演示一遍  
在fofa2xray目录下打开一个cmd，其次运行fofa2xray.exe  
如下图所示：

![](https://image.3001.net/images/20210201/1612156780_60178f6c4640ded00075b.png!small)

![](https://image.3001.net/images/20210201/1612156781_60178f6d133de4e67c4ed.png!small)脚本会啪啦啪啦地执行  
回到fofa2Xray的目录下你会发现，根据配置文件的fofa语句规则生成好了相对于的文件

![](https://image.3001.net/images/20210201/1612156781_60178f6ddf0390363d050.png!small)这个文件是用来给Xray扫到网站漏洞存放报告的路径，等他扫完之后就会在里面生成一个一个的漏洞报告文件，默认格式是html的

![](https://image.3001.net/images/20210201/1612156782_60178f6e9369beacde83e.png!small)如果文中有错的地方或者不对的地方，可以联系我进行修改喔，非常感谢！  
QQ：3566163660  
补充：如果是普通用户的话fofa能保存下来的查询结果并不多，如果是普通会员就刚好够用了~~

