## 一、背景

 **上周有朋友反映一台服务器流量超标， 怀疑中木马，请求帮忙处理，平时长期在应用层打杂习惯了，其实并没有什么底气去排查系统底层后门这些东西
。但是既然有需求，当然还是尽力去解决。当然这一过程也受益匪浅，就和大家分享一下。**

## 二、发现和追踪过程

1\. 查看系统状态信息发现问题

发现目标主机存在可疑IP连接信息

![image.png](https://image.3001.net/images/20180423/15244894045177.png!small)![image.png](https://image.3001.net/images/20180423/15244894116536.png!small)![image.png](https://image.3001.net/images/20180423/15244894207719.png!small)![image.png](https://image.3001.net/images/20180423/15244894254001.png!small)  

经排查系tmp目录下的可疑文件Welcom运行，同时发现了复制在bin目录下的双胞胎。  

2\. top动态查看进程，确定果然是/tmp/Welcom这玩意在搞怪  

**![image.png](https://image.3001.net/images/20180423/15244894647457.png!small)  
**

3. 拉下来稍微研究了下，逆向能力一般，只能最简单的看了看 **  
**

![image.png](https://image.3001.net/images/20180423/15244895057954.png!small)  

各位可自行去拉取脚本

![image.png](https://image.3001.net/images/20180423/15244895278415.png!small)  

看行为应该是挺典型的minerd挖矿程序，应该是做过变异，哈勃竟然查不出来问题。  

![image.png](https://image.3001.net/images/20180423/15244895467169.png!small)  

后边用其他引擎扫了扫基本也能确定类型  

![image.png](https://image.3001.net/images/20180423/15244895727668.png!small)![image.png](https://image.3001.net/images/20180423/15244895835304.png!small)  

4、根据恶意程序的脚本，去查看系统定时任务  

**![image.png](https://image.3001.net/images/20180423/15244896222259.png!small)**

根据排查，恶意程序的感染时间较久，根据文件用户属性应是来源于最初的Tomcat所属权限的用户，可能是通过前期低版本的Tomcat服务器漏洞被利用导致，后来以root用户运行了Tomcat导致感染了root用户。（最初的症状就是一开启Tomcat就流量超标）。  

## 三、清理方案

1\. 清除主机上所有的非自主设置定时任务；

2\. 清除/tmp目录下可疑文件，该目录为临时文件，建议不需要的都可清理

3\. 清除Bin目录下Welcom文件

4\. 清除/var/spool/cron/rootc文件

5\. 清除/etc/wnell

6\. 杀死Welcom进程（pkill Welcom观察一段时间是否有重启迹象）

7\. Iptalbless或防火墙策略限制对恶意IP：45.76.78.9和域名的连接<http://love.suime.win/>
(无法第一时间清除程序或无法保证清除干净的双保险)

8\. 删除系统中不用的账户

9\. 关闭不需要的端口和服务，卸载不需要的组件如samba

10\. 升级openssh到最新版本、Tomcat也及时升级最新版本（不建议使用root用户权限启动tomcat）

11\. 排查/root/.ssh/目录下是否都是信任的主机，排除内网已有其他主机被攻击作为跳板机的可能。

## 附录（顺道发现的DDoS后门）：

在排查开机启动项时，发现/etc/init.d明显两个时间和长相都很怪异的文件，其实在清理/tmp目录时候已经怀疑了/tmp/phpsos，就扔给一位逆向大牛同事分析了下，说是很明显的DDoS.  

![image.png](https://image.3001.net/images/20180423/15244898603967.png!small)

![image.png](https://image.3001.net/images/20180423/15244898697539.png!small)  

后来查了下，这类木马比较常见，分享一下当时我用的笨方法比较快速的清除，

1.根据发现的那两个恶意文件入侵时间定位了那个时间点被修改的所有文件(很常见的替换ps和netstat...)

![image.png](https://image.3001.net/images/20180423/15244899433363.png!small)  

2\. 根据文件的大小，找出所有木马主运行程序  

![image.png](https://image.3001.net/images/20180423/15244899599567.png!small)  

其实刚刚才知道可以根据文件字节大小直接查找同样大小的文件 find / -size 1223123c  

清除结束后最后还得copy或者重装正常的系统命令。

 ***本文作者：弹指江山，转载请注明来自FreeBuf.COM**

