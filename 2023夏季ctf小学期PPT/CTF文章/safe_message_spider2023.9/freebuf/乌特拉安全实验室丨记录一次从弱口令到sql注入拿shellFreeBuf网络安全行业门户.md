## **0x00 前言**

有段时间一直在挖 edu，挖到一个从普通用户权限到 getshell
的站，觉得挺有意义的，记录了一下，也学到了挺多知识的，但中间也出现了些小插曲，有个地方没弄明白，就一直没发文章，最近通过某不知名大佬的帮助下已经弄懂了，所以前来发个文章。

##  **0x01 爆破**

回顾当初打开是一个登录页面：![](https://image.3001.net/images/20220428/1651126638_626a316e93b44772bf05f.png!small)  
随便登录一下发现用户名可爆破：![](https://image.3001.net/images/20220428/1651126671_626a318f29dca3fb90d43.png!small)  
进行爆破得到一个普通用户的账户名和密码：![](https://image.3001.net/images/20220428/1651126700_626a31acc058d0a781cd1.png!small)

##  **0x02 后台注入**

登录进去发现在查找搜索框处存在sql注入漏洞：

![](https://image.3001.net/images/20220510/1652168075_627a158b7cdfe5af5c53a.png!small)  
![](https://image.3001.net/images/20220428/1651126746_626a31da3506f81491a6a.png!small)并且是dba权限的：  
![](https://image.3001.net/images/20220428/1651126772_626a31f407f55768ad3e8.png!small)

##  **0x03 尝试写shell**

起初尝试寻找网站路径写个 shell，然后中间出现了些小插曲，一开始我不知道如何寻找目录，在请教 adminxe 大佬后，大佬给了几条命令。

  

查找文件：

for /r D:\ %i in (匹配模式1,匹配模式2) do @echo %i

for /r D:\ %i in (*.aspx) do @echo %i

  

查看盘符：

1）使用diskpart命令查看

diskpartlist volume

2）使用fsutil查看

fsutil volume list

3） 使用wmic命令查看

wmic logicaldisk get caption,name

  

经过尝试发现不行，几乎所有的文件夹都存在我寻找的那个文件。

类似于这样：

![](https://image.3001.net/images/20220428/1651126802_626a3212aad6962eb613b.png!small)

##  **0x04 反弹shell**

通过sql注入 os shell 利用 cs 进行 powershell 反弹 shell 成功。

![](https://image.3001.net/images/20220428/1651126829_626a322d88b527ad0a75a.png!small)

##  **0x05 再次尝试shell成功**

后来经某不知名大佬的研究发现，之所以可以用 cs 反弹 shell，是因为网站没有 waf，如果不能上线
cs，该怎么做？还是需要获取路径，某不知名大佬考虑通过 dir | find 或者 for 命令查找网页名字或者 css 名字来寻找路径。

  

最终某不知名大佬的研究发现可以使用 for 命令来寻找路径：

for /r C:// %i in (*文件名字) do @echo %i

  

这里需要猜测盘符，以及*很重要，如果没有*，找到的文件和我之前的一样， 几乎所有文件夹都有我们寻找的那个文件。

![](https://image.3001.net/images/20220428/1651126859_626a324b60bddd6215a2c.png!small)有了*，找到的文件是这样的：![](https://image.3001.net/images/20220428/1651126878_626a325ec83e08248cc47.png!small)  
找到的目录只有三个，可以很快判断文件目录，因为不是时间注入，查找的速度还行，十秒不到就出来了。直接 echo 一句话，掏出蚁剑获取 webshell
成功。![](https://image.3001.net/images/20220428/1651126903_626a32773ed31d02f53b9.png!small)  
  
  
  

