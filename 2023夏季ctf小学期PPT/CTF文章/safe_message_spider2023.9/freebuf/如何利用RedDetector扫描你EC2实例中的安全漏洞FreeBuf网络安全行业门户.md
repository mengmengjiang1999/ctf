![](https://image.3001.net/images/20210513/1620894667_609ce3cb2ec7d311039e1.png!small)

## 关于Red-Detector

Red-Detector是一款功能强大的安全扫描工具，该工具可以帮助广大研究人员利用vuls.io扫描EC2实例中的安全漏洞。该工具主要基于[
_Vuls_](https://vuls.io/en/)实现其漏洞扫描功能，基于 _Lynis_来寻找EC2实例中的安全错误配置，并利用[
_Chkrootkit_](http://www.chkrootkit.org/)扫描EC2实例中的rootkit签名。

## 工具要求

1、使用下面列出的EC2 Action配置你的AWS账号，大家可以在项目中下的red-detector-policy.json文件中找到相关的权限要求：

> AttachVolume
>
> AuthorizeSecurityGroupIngress
>
> DescribeInstances
>
> CreateKeyPair
>
> CreateTags
>
> DescribeRegions
>
> RunInstances
>
> ReportInstanceStatus
>
> DescribeSnapshots
>
> DescribeImages
>
> DescribeVolumeStatus
>
> DescribeVolumes
>
> CreateVolume
>
> DescribeAvailabilityZones
>
> DescribeVpcs
>
> CreateSecurityGroup
>
> CreateSnapshot
>
> DeleteSnapshot

2、运行EC2实例-确保你已经知道待扫描EC2实例的地区以及实例ID，支持的版本如下：

> Ubuntu: 14, 16, 18, 19, 20
>
> Debian: 6, 8, 9
>
> Redhat: 7, 8
>
> Suse: 12
>
> Amazon: 2
>
> Oracle: 8

## 工具安装

首先，广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    sudo git clone https://github.com/lightspin-tech/red-detector.git

接下来，切换到本地项目目录下运行下列命令安装依赖组件：

    
    
    pip3 install -r requirements.txt

## 工具使用

### 交互式使用

    
    
    python3 main.py

### 命令参数

    
    
    usage: main.py [-h] [--region REGION] [--instance-id INSTANCE_ID] [--keypair KEYPAIR] [--log-level LOG_LEVEL]
    
     
    
    optional arguments:
    
      -h, --help                show this help message and exit
    
      --region REGION           region name
    
      --instance-id INSTANCE_ID EC2 instance id
    
      --keypair KEYPAIR         existing key pair name
    
      --log-level LOG_LEVEL log level

### 使用流程

> 运行py。
>
> 地区选择：使用默认地区（us-east-1）或选择一个地区，如果选择的地区不包含任何EC2实例的话，你将需要选择其他地区。
>
> EC2实例ID选择：你将会获取到所选地区中所有的EC2实例列表，接下来需要选择一个待扫描的实例，确保选择的是一个可用实例ID。
>
> 跟踪工具扫描进程，大约需要30分钟扫描时间。
>
> 获取报告链接。

## 工具运行演示

![](https://image.3001.net/images/20210513/1620894722_609ce402f0f0fd0708eef.gif!small)

## 许可证协议

本项目的开发与发布遵循Apache v2.0开源许可证协议。

## 项目地址

Red-Detector：【[ _GitHub传送门_](https://github.com/lightspin-tech/red-detector)】

