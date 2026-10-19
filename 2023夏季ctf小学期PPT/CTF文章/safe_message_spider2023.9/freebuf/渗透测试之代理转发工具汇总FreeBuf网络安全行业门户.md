类型| 名称| 需要VPS| 格式| 特点| 备注| | |  
---|---|---|---|---|---|---|---|---  
端口转发| LCX| yes| exe| RDP3389反弹，简单方便，使用频率高| | | Proxifier| 全局代理  
rtcp| yes| py| SSH22反弹常用| | | SocksCap64| 部分应用代理  
Fpipe| yes| exe| 多端口转发| | | proxychains | 部分应用代理  
antifw| no| exe| 停掉IIS动作有点大| | | |  
Tunna| no| py| 正向代理  
需上传shell；22&3389均可；亦可代理内网其他主机；  
速度有点慢。| | | |  
reDuh| no| java| 正向代理；  
需上传shell；22&3389均可；亦可代理内网其他主机；| | | |  
ssocks| yes| py| 有windows版：Ssock_win.exe  
linux 需编译安装；  
结合proxychains使用；| | | |  
web代理| reGeorg| no| py| 正向代理  
需上传shell且需配Proxifier；  
内网渗透必备即使尚未提权。| reGeorg是reDuh的继承者，利用了会话层的socks5协议，效率更高。| | |  
Phpsocks| no| php| 不好用，有局限| | | |  
s5.py| no| py| web代理，简单方便快捷| [ringzero@557.im](mailto:ringzero@557.im)| | |  
htran| yes| exe| 正向代理/反向代理  
正反向端口转发| 正向代理不需要自己VPS| | |  
EarthWorm| yes| C| 支持多平台；  
正向代理、反向代理；  
多重网络应用  
很好用。| 正向代理不需要自己VPS  
Termite| | |  
shell反弹| ssh bash nc py| yes| -| 频率最高| | | |  
php jsp perl ruby lua| -| -| 看需求点| | | |  
VPN| -| -| 看需求点| | | |  
meterpreter| -| -| msf 套装| | | |

