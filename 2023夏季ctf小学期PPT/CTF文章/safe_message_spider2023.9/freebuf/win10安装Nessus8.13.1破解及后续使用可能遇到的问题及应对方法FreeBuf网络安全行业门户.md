## 前言：

1，之前安装的8.2的版本，失败了，后来找的8.13.1版本。

2，尝试破解8.13.1，成功了，参照的8.12破解方式。（猜测8版本的破解手段大致相同，不过8.2使用的别人的，失败了）

3，遇到的问题在文章：学习遇到的问题，里面有，后面找到问题原因，在评论里面追加。

4，啰嗦了这么多，下面直入正题。

## 安装：

有的部分就不附图了，自己多动动手哈~。

  * 0x1 准备阶段：  
1，通过 Nessus官方 下载安装包--Nessus-8.13.1-x64.msi  
2，通过 Nessus官方渠道 提交试用信息（申请注册），之后邮箱会收到激活码(activation code)  
NEYP-JJ4V-Z**B-VECJ-K***  
3，双击安装包Nessus-8.13.1-x64.msi进行安装（改了路径一定要记住自己 **安装的路径** ）

0x2 安装配置：  
1，安装成功后，Nessus会自动打开浏览器，进入欢迎配置页，选择Managed Scanner并点击Continue  
2，选择Tenable.sc并点击Continue  
3，设置账户密码并点击Submit（记住，以后登录用）  
4，完成配置后，将进入Nessus设置页（没啥用，多点点，看下nessus状态，信息）

0x3 离线激活  
1，获得询问码(challenge code)  
使用 **管理员权限**
运行命令行，进入到Nessus安装目录后（nessuscli.exe这个文件所在目录），使用该命令获得询问码：nessuscli.exe fetch
--challenge  
运行结果：Challenge code:
377e*****de1a1b4bbd46f*****ee0edd087ce85d（把这个code后面的这一串询问码保存好，后面有用）

2，进入 离线激活页面 ，输入最开始邮件得到的激活码和询问码，点击Submit获得离线插件包和激活证书。（保存好 **证书** ，或者不要关闭这个页面都行）  
\-----BEGIN TENABLE LICENSE-----  
.............略

.........略  
\-----END TENABLE LICENSE-----
3，点击页面上的链接下载得到all-2.0.tar.gz插件包， **把all-2.0.tar.gz复制到nessus的安装目录**
，接着获取询问码的命令行，安装插件包  
nessuscli.exe update all-2.0.tar.gz（管理员权限运行命令行cmd，进入到Nessus安装目录后执行。注意下路径问题）  
结果：Copying templates version **202103191032** to
D:\xxx\Tenable\Nessus\nessus\templates\tmp  
4，保存结果中的数字串 **202103191032** ，后面会用到（最好整个txt,把相关重要信息记录下来）  
5，回到Nessus设置页，Activation Code 还是 N/A，没关系，点击旁边的小笔

