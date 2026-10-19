**今天给大家介绍的是一款名叫Legion的开源软件，这款工具简单易用，且具有高度可扩展性。这是一款半自动化的网络渗透测试工具，可帮助研究人员发现、侦察和利用目标信息系统中的安全漏洞。**

![1.png](https://image.3001.net/images/20190313/1552466218_5c88c12a21c71.png!small)

## 功能介绍

1、
使用NMAP、whataweb、nikto、Vulners、Hydra、SMBenum、dirbuster、sslyzer和webslayer等工具（大约100多个自动化脚本）实现自动化网络侦察和扫描。

2、 提供了易于使用的图形化操作界面，丰富的菜单选项，以及多功能操作面板，允许渗透测试人员快速寻找并利用目标主机中的漏洞。

3、 模块化功能允许用户轻松对Legion进行定制开发，或自动化调用自己的脚本。

4、 高度定制化扫描阶段，以躲避IPS。

5、 自动化扫描CPE和CVE。

6、 实时自动保存扫描结果和任务进展。

### 功能升级

1、 项目代码进行了重构，代码升级为Python 3.6，并最小化了工具所需的额外代码库。

2、 升级至了PyQT5，增强了工具的响应性，减少了Bug，提升了GUI界面。

3、 支持主机名解析和vhosts/sni主机扫描功能。

4、 修改进程队列和程序执行机制，提升了应用程序的性能以及稳定性。

5、 通过依赖解析和自动化安装脚本简化了程序的安装过程。

6、 项目实时自动保存，即使在任务出错的情况下我们也不会丢失任何数据。

7、 Docker容器部署功能。

8、 高度活跃的开发团队提供支持。

## 工具安装  

### 传统方式

假设你使用的设备为Ubuntu、Kali或Parrot Linux，且系统已安装了Python
3.6，那么该工具所需的其他依赖组件将能够自动完成安装。终端命令如下：

    
    
    git clone <https://github.com/GoVanguard/legion.git>
    
    cd legion
    
    sudo chmod +x startLegion.sh
    
    sudo ./startLegion.sh

### Docker方式

假设你的设备上已安装了Docker和Xauthority，那么在终端运行下列命令即可：

    
    
    git clone <https://github.com/GoVanguard/legion.git>
    
    cd legion/docker
    
    sudo chmod +x runIt.sh
    
    sudo ./runIt.sh

## 许可证协议

Legion遵循[GNU General
Publicv3.0](https://github.com/GoVanguard/legion/blob/master/LICENSE)许可证协议。

***参考来源：[legion](https://github.com/GoVanguard/legion/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

