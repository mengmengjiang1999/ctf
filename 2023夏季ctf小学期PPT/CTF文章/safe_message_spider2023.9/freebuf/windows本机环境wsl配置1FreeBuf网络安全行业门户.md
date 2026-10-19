当个备份的博客笔记，希望师傅们，如果以后同一网段的时候 不要来日我  
![图片.png](https://image.3001.net/images/20210804/1628068061_610a58dd7a83ada691df0.png!small)或许可能以后更新的文章类型，实战类，渗透测试类就比较少了，具体原因
不用多说，还是更偏向ctf 靶场或者 其他更多的技术类的

不是实战不搞 ，也就是私下里自己搞了，当然必须是有授权的

个人感觉ctf和web实战 渗透 主要可能还是 思路 侧重的地方不同

ctf偏向研究，一些文件权限啊，linux

不过要是深入研究的话 到内网 那可能又要掌握更多的东西

个人小白观点而已，或许以现在的垃圾的水平 眼界还看的不够清楚

这次是去找一个保存文件 自动运行一行shell的编辑器，sublime text 没有找到，如果有师傅知道 麻烦告诉我下

notepad++

简称npp

插件-nppexec-adcanced options  
![图片.png](https://image.3001.net/images/20210804/1628068088_610a58f8707af77a43ef4.png!small)![图片.png](https://image.3001.net/images/20210804/1628068095_610a58ffe333d65baaf57.png!small)![图片.png](https://image.3001.net/images/20210804/1628068103_610a5907f0a2b37dc4a9f.png!small)execute  
![图片.png](https://image.3001.net/images/20210804/1628068114_610a59121ef7765d2df10.png!small)

    
    
    NPP_SAVE
    cd $(CURRENT_DIRECTORY)
    wsl chmod -R 777 /var/www/html/t1
    

![图片.png](https://image.3001.net/images/20210804/1628068141_610a592d1a0b49808ea04.png!small)清空save
delete  
![图片.png](https://image.3001.net/images/20210804/1628068150_610a5936c270cf6a86c89.png!small)

    
    
    cd $(CURRENT_DIRECTORY)
    D:\phpstudy_pro\Extensions\php\php7.4.3nts\php.exe $(FULL_CURRENT_PATH)
    
    php74环境 windows的环境 借用phpstudy的php74
    

save_chmod_777_var_www_html

![图片.png](https://image.3001.net/images/20210804/1628068176_610a59501b094ac28fbff.png!small)快捷键管理  
![图片.png](https://image.3001.net/images/20210804/1628068186_610a595ab4fc31671ba85.png!small)![图片.png](https://image.3001.net/images/20210804/1628068194_610a596230dd58001b4ee.png!small)右键  
![图片.png](https://image.3001.net/images/20210804/1628068205_610a596d7e4b628b339df.png!small)clear

切换插件命令  
![图片.png](https://image.3001.net/images/20210804/1628068287_610a59bfccf4ff5e2d851.png!small)modify修改  
每次保存文件 自动 运行 命令  
自动运行  
wsl chmod -R 777 /var/www/html/t1  
此条命令  
本机wsl设置  
![图片.png](https://image.3001.net/images/20210804/1628068307_610a59d3cb7db7a964145.png!small)默认wsl环境就是  
ubuntu 20版本的 wsl1

在wsl-1 ubuntu20  
windows找到对应的目录 用Windows本机创建一个文件  
哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈.txt  
![图片.png](https://image.3001.net/images/20210804/1628068322_610a59e2beb63571a318e.png!small)可以发现文件权限是-----  
当 wsl玩web环境的时候  
在/var/www/html下源码  
我们可以在windows本机修改源代码 但是 一经过windows本机的编辑器  
比如 notepad 或者 sublime text 保存 文件权限就变了  
变得无法访问 ，apche2+php  
比如你写了一个

    
    
    <?php
    phpinfo();
    ?>
    

phpinfo.php  
文件权限不够 连rrr的权限都没有 连读的权限都没有 就会返回一片空白  
![图片.png](https://image.3001.net/images/20210804/1628068365_610a5a0da75dbd97d8e37.png!small)![图片.png](https://image.3001.net/images/20210804/1628068375_610a5a17cdf3de88245e8.png!small)windows本机随便操作一下保存  
![图片.png](https://image.3001.net/images/20210804/1628068385_610a5a2196e909166abe1.png!small)然后文件权限变成了
----  
然后  
![图片.png](https://image.3001.net/images/20210804/1628068400_610a5a3090009d2e5401b.png!small)我开启了报错信息  
如果不开启报错信息的话 会是一片空白  
这里还发现一点  
![图片.png](https://image.3001.net/images/20210804/1628068413_610a5a3df3f56a3ffd969.png!small)同时我wsl1和wsl2
都是ubuntu20 都开启了apache2  
并且 端口都是设置成了10080 发现可以共同开启  
没有端口冲突之类的  
也好理解  
wsl2的ubuntu20相当于虚拟机  
wsl1的ubuntu20相当于本机  
当然不同了  
wsl2 ubuntu20执行ifconfig  
![图片.png](https://image.3001.net/images/20210804/1628068429_610a5a4d4a0d5f4ff3902.png!small)wsl1下的
ubuntu20 执行ifconfig  
![图片.png](https://image.3001.net/images/20210804/1628068464_610a5a709dbe37da4354d.png!small)看长度就可以看出来了  
wsl1下的 ifconfig  
在wsl2下没有这个问题  
也好理解  
![图片.png](https://image.3001.net/images/20210804/1628068485_610a5a856955357f271cb.png!small)这里网上师傅们写的东西很多了
就不啰嗦了  
https://mks.tw/3343/windows-%E7%82%BA%E4%BB%80%E9%BA%BC%E9%81%B8%E6%93%87%E5%BE%9E-wsl2-%E9%99%8D%E5%9B%9E-wsl1  
https://www.cnblogs.com/stulzq/p/13926936.html  
https://www.v2ex.com/t/587642  
https://blog.csdn.net/weixin_33929779/article/details/112238216  
https://docs.microsoft.com/zh-tw/windows/wsl/compare-versions  
https://www.zhihu.com/question/424191615/answer/1842582111  
https://zhuanlan.zhihu.com/p/356397851  
![图片.png](https://image.3001.net/images/20210804/1628068506_610a5a9a5e4cd6f9d10d9.png!small)我已经在期待wsl3了
不知道 有没有 类似华为5g研发的俄罗斯小伙，天才 能想出一些解决方法 或许将会是革命性的，从更底层 硬件  
可以发现wsl2 的ubuntu20  
![图片.png](https://image.3001.net/images/20210804/1628068519_610a5aa70ce5a4da78566.png!small)本机windows
创建的文件权限  
![图片.png](https://image.3001.net/images/20210804/1628068529_610a5ab17e359502013a3.png!small)与
直接 touch 123321创建的文件 权限是一样的  
是rw r r  
wsl2无法修改 文件夹颜色  
wsl1可以  
两者都是ubuntu20  
https://docs.microsoft.com/zh-cn/windows/wsl/file-permissions  
目前以使用xrdp windows自带远程管理桌面  
win+r  
mstsc  
localhost:3390  
localhost:xxxx端口  
![图片.png](https://image.3001.net/images/20210804/1628068547_610a5ac378cce100afd6a.png!small)输入用户名密码即可

简单修改了下样子  
![图片.png](https://image.3001.net/images/20210804/1628068556_610a5acc6e798c0b459d1.png!small)![图片.png](https://image.3001.net/images/20210804/1628068561_610a5ad13d86ef792c160.png!small)![图片.png](https://image.3001.net/images/20210804/1628068565_610a5ad5de2a059768351.png!small)

