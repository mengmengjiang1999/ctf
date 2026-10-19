## 靶机介绍

DC-5 is another purposely built vulnerable lab with the intent of gaining
experience in the world of penetration testing.

The plan was for DC-5 to kick it up a notch, so this might not be great for
beginners, but should be ok for people with intermediate or better experience.
Time will tell (as will feedback).

靶机地址：https://www.vulnhub.com/entry/dc-5,314/

##
[](https://zhuanlan.kanxue.com/article-10580.htm#%E5%AD%A6%E4%B9%A0%E5%88%B0%E7%9A%84%E7%9F%A5%E8%AF%86)学习到的知识

`LFI`(本地文件包含)日志获取shell  
`wfuzz`工具的使用  
`screen`提权root

##
[](https://zhuanlan.kanxue.com/article-10580.htm#%E4%BF%A1%E6%81%AF%E6%90%9C%E9%9B%86)信息搜集

拿到 `IP` 先扫描端口开放服务：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1222.png)

它这边只开放了 `80`（http）和 `111`（RPC）两个端口服务！

RPC 他是一个`RPC`服务，主要是在`nfs`共享时候负责通知客户端，服务器的`nfs`端口号的。简单理解`rpc`就是一个中介服务。

我们先来到 `WEB` 端，但是没有什么可利用点，只有一个表单提交的地方：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1223.png)

我随便提交了一些内容，发现了它会被提交到 `thankyou.php` 这个文件：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1224.png)

##
[](https://zhuanlan.kanxue.com/article-10580.htm#lfi%E6%9C%AC%E5%9C%B0%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB%E8%8E%B7%E5%8F%96shell)LFI本地文件包含获取shell

看上去有点像 `LFI`（本地文件包含）漏洞，紧接着我用 KALI 自带的 wfuz 工具对它一顿FUZZ**：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1225.png)

由于`FUZZ`出来的参数太多了！而且好多都没有，我两眼一迷的仔细找到了一个参数：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1226.png)

打开后我发现它可以读取系统文件：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1227.png)

这个时候确定了它存在本地文件包含！那么我继续用 `wfuzz` 缩小我们得到的参数范围：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1228.png)

这样我们就成功的得到一些可利用的参数：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1229.png)

随后我发现了它的一个日志文件里有我们的请求记录：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1230.png)

既然日志能记录我们的操作，那么我们就写入一句话到日志文件里吧：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1231.png)

(温馨提示：到这里我靶机重启了一下，所以 IP 变了)

接下来然后用日志文件去执行命令 `ls`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1232.png)

成功执行命令！那么我就用 `nc` 反弹一个`shell`回来吧！先是 KALI `nc` 监听 `5555` 端口，然后访问得到一枚 `shell`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1233.png)

得到 shell 以后我用 `python` 切换到 `bash`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1234.png)

##
[](https://zhuanlan.kanxue.com/article-10580.htm#%E6%9D%83%E9%99%90%E6%8F%90%E5%8D%87)权限提升

之后我查找 `SUID` 权限的文件发现了 `screen` ：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1235.png)

紧接着我又去搜索了一下关于 `screen` 的漏洞，找到了一个提权 `poc`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1236.png)

接着我按照上面的 `POC` 创建了 `libhax.c`、`rootshell.c` 文件，文件内容是：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1237.png)

随后用 `gcc` 编译他们：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1238.png)

编译完后我用 `nc` 把刚刚编译好的文件传到目标服务器上：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1239.png)

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1240.png)

最后按照 `POC` 上面的步骤依次输入命令提权为 `root`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1241.png)

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1242.png)

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1243.png)

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1244.png)

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1245.png)

最终也是在 `/root` 目录下拿到了 `Flag`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1246.png)

公众号：Gcow安全团队  
![](https://zhuanlan.kanxue.com/upload/attach/20200304/879321_EMBMDE87TKC6436.jpg)

  

