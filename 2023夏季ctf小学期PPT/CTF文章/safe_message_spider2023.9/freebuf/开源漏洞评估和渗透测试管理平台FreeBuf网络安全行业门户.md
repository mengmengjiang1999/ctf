## 简介

Reconmap 是一个漏洞评估和渗透测试 (VAPT)
平台。它帮助软件工程师和信息安全专业人员在安全项目上进行协作，从规划到实施和输出文档。该工具的目标是在尽可能短的时间内从侦察到输出报告。

## 安装

### 一．从github（https://github.com/reconmap/reconmap）拉取文件：

进入reconmap目录,docker-compose up -d,如图2-1所示

![](https://image.3001.net/images/20210805/1628127718_610b41e651d558a7c48fe.png!small)

图2-1，docker运行

### 二．打开浏览器访问http://localhost:3001，如图2-2所示

![](https://image.3001.net/images/20210805/1628127767_610b4217220a606c3ab68.png!small)

图2-2

注：localhost替换成本地ip。docker启动时可能会遇到图2-3 redis默认端口6379被占用的情况，解决如图2-4（参考：[
_https://blog.csdn.net/qq_17623363/article/details/106436394_](https://blog.csdn.net/qq_17623363/article/details/106436394)）

![](https://image.3001.net/images/20210805/1628127801_610b4239ec751317abf36.png!small)

图2-3 redis端口被占用

![](https://image.3001.net/images/20210805/1628127825_610b4251dd46ee72b56b7.png!small)

图2-4 关掉本地redis服务

### 三．需要搭配reconmap cli一起使用

从GitHub(https://github.com/reconmap/cli)拉取文件，进入cli目录执行make命令如图2-5会出现超时，解决见注。

![](https://image.3001.net/images/20210805/1628127886_610b428e1ae5eafd175b5.png!small)

图2-5

注：执行代理即可解决

go env -w GO111MODULE=on

go env -w GOPROXY=https://goproxy.io,direct

然后配置config如图2-6，登录如图2-7即可使用

![](https://image.3001.net/images/20210805/1628127924_610b42b4aa57277a7d462.png!small)

图2-6 配置config

![](https://image.3001.net/images/20210805/1628127956_610b42d488446e974f03a.png!small)

图2-7 登录

## 功能简介

### 大屏幕展示

如图3-1，直观的展示当前任务状态，一段时间内的用户活动情况，漏洞威胁程度占比，漏洞类别，以及最常用到的命令排行。

![](https://image.3001.net/images/20210805/1628128032_610b43209a82a35816fcb.png!small)

图3-1 大屏幕展示

### 创建项目

如图3-2，填写对应内容信息创建项目。

![](https://image.3001.net/images/20210805/1628128090_610b435a42050fa4b233d.png!small)

图3-2创建项目

如图3-3项目创建成功

![](https://image.3001.net/images/20210805/1628128168_610b43a8e3ff22bea4524.png!small)

图3-3 项目创建成功

### 创建任务

如图3-4选择nmap命令

![](https://image.3001.net/images/20210805/1628128214_610b43d6b0a669d57b5ac.png!small)

图3-4 选择nmap

如图3-5复制命令到cli执行

![](https://image.3001.net/images/20210805/1628128259_610b4403201b5e83d688f.png!small)

图3-5 命令指导

如图3-6可以看到nmap扫描的结果已经上传到web端。

![](https://image.3001.net/images/20210805/1628128292_610b4424284b5b009f2ae.png!small)

图3-6 扫描结果已经上传到web端

如图3-7，利用该平台可以上传结果直接导出评估报告，这些报告既可以在信息安全团队内部使用，也可以交给客户。

![](https://image.3001.net/images/20210805/1628128350_610b445ee9688f857c026.png!small)

图3-7，导出评估报告

### demo演示平台

reconmap官方给出了一个实时演示地址，更多的功能在如下地址中探索：[
_https://demo.reconmap.org_](https://demo.reconmap.org)账号： **admin** ，密码：
**admin123。**

