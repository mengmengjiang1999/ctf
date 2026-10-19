![](https://image.3001.net/images/20210917/1631892753_6144b511f11eef6824058.jpg!small)

## 关于BeaconEye

BeaconEye是一款针对CobaltStrike的安全工具，该工具可以扫描正在运行的主动CobaltStrike
Beacon。当BeaconEye扫描到了正在运行Beacon的进程之后，BeaconEye将会监控每一个进程以查看C2活动。

## 工作机制

BeaconEye将会扫描活动进程或MiniDump文件，以尝试检测CobaltStrike Beacon。在活动进程模式下，CobaltStrike
Beacon可以将其以调试器的身份与目标进程绑定，监控Beacon活动以识别C2流量（当前版本的BeaconEye支持HTTP/HTTPS Beacon）。

用于加密C2数据和mallable配置文件的AES密钥会被动态解码，这将允许BeaconEye能够在操作人员发送命令时提取和解密Beacon的输出。

每个进程都会创建一个活动日志文件夹，该文件夹与执行BeaconEye的当前目录对应。

## 功能介绍

每个进程一个日志文件夹；

导出Beacon配置；

显示大多数Beacon命令的输出；

保存屏幕截图；

检测单独的和注入的Beacon；

检测使用内置sleep_mask隐藏的Beacon；

扫描正在运行的进程或离线Minidump文件；

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CCob/BeaconEye.git

## 工具使用

    
    
    BeconEye by @_EthicalChaos_
    
      CobaltStrike beacon hunter and command monitoring tool x86_64
    
     
    
      -v, --verbose              开启Verbose模式，显示更多信息
    
      -m, --monitor             扫描正在运行的活动进程，与之进行绑定并监控
    
      -f, --filter=VALUE           使用名字过滤进程列表（仅活动模式下可用）
    
      -d, --dump=VALUE          Minidump模式专用目录（*.dmp或*.mdmp）
    
      -h, --help                 显示帮助信息

## 注意事项

BeaconEye可以检测所有Beacon类型，但只能监控HTTP/HTTPS Beacon。目前，工具只会解码命令输出数据，而不会解码命令请求。

## 项目地址

 **BeaconEye：** 【[ _GitHub传送门_](https://github.com/CCob/BeaconEye)】

## 参考资料

> [
> _https://github.com/Apr4h/CobaltStrikeScan_](https://github.com/Apr4h/CobaltStrikeScan)
>
> [
> _https://www.freebuf.com/articles/network/288210.html﻿_](https://www.freebuf.com/articles/network/288210.html)

