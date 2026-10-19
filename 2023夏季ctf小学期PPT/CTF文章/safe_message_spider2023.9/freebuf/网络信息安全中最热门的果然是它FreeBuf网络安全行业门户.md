昨天的问卷调查发布后，我们收到了大家的积极反馈，看到了很多用心的留言回复，小编真的特别感动，再次感谢所有参与投票的小伙伴们！（搜索i春秋公众号进行投票）

投票仍在继续，公众号会根据最后的结果进行数据分析，从而做出相应调整，尽最大努力去满足大家的要求。

![1.png](https://image.3001.net/images/20181206/1544084433_5c08dbd1ea594.png!small)目前从现有的数据来看，大家对于技术类的文章，偏爱Web安全内容的人更多一些，所以今天我们就从Web安全的技术内容出发，分享的是
**刺透内网的HTTP代理** 的相关内容，希望对大家有所帮助。

 **从偶然出发**  

**![2.png](https://image.3001.net/images/20181206/1544084591_5c08dc6fd5cdc.png!small)
**从被动偶然到主动发现**  
**

 **
**![3.png](https://image.3001.net/images/20181206/1544084623_5c08dc8f89807.png!small)![4.png](https://image.3001.net/images/20181206/1544084673_5c08dcc188389.png!small)
**主动发现脚本开发**  
****

脚本语言选择：python2.7

系统环境：all

 **思考**

如何判断这个网站存在可以作为HTTP代理访问资源？唯一特征是什么？  

脑子中唯一的思路就是IP，如果这目标站点能作为HTTP代理访问资源，那么我设置的这个资源就是返回真实IP的，这样就可以判断了。

这里我在团队官网上小小的写了一个，但是在大批量去测试却无法使用，因为官网的空间没那么大的吞吐量，承载不住高并发，后期建议大家使用
http://httpbin.org/ip 这个接口。

http://www.hi-ourlife.com/getip.php

PHP代码：

 ** **
**![5.png](https://image.3001.net/images/20181206/1544084733_5c08dcfd8fd1a.png!small)![6.png](https://image.3001.net/images/20181206/1544084775_5c08dd27d7482.png!small)![7.png](https://image.3001.net/images/20181206/1544084810_5c08dd4a5083a.png!small)![8.png](https://image.3001.net/images/20181206/1544084850_5c08dd726c9df.png!small)![9.png](https://image.3001.net/images/20181206/1544084881_5c08dd919166f.png!small)
**最后**  
******

使用方法：python proxy_vul.py urls.txt

urls.txt 格式：

http://www.hi-ourlife.com/

https://gh0st.cn/

http://mst.hi-ourlife.com:8080/

建议批量方法：

扫描所有想检测站点的web服务端口（Nginx容器存在此类问题居多），然后使用脚本检测。

 ** ** ** **  
********

