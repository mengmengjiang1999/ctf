![a.png](https://image.3001.net/images/20190517/1558057536_5cde12401f7a3.png!small)

## iCULeak

**该工具可以从思科CUCM管理环境中的手机配置文件内搜索并提取用户的凭证数据。在使用思科的CUCM（拨号管理器）时，手机配置文件会存储在一台TFTP服务器中，这些VoIP通话配置文件中通常都会包含很多敏感数据，其中包括手机的SSH或管理员凭证。**

大家知道浏览器如何利用CUCM凭证来自动填写类似SSH用户名&密码这样的表单域吗？如果管理员在他们的浏览器中保存了凭证，那么问题就转移到了他们如何使用密码管理器之类的自动填写插件来保存凭证数据了。但无论如何，只要他们使用了自动填写功能，SSH或管理员账号的用户名及密码就会以明文形式存储在手机配置文件中。

注意：即使时思科发布了CUCM v12.0来修复这个安全问题，我们仍然是可以找到存储在手机里的凭证数据的。

## 工具安装

    
    
    git clone <https://github.com/llt4l/iCULeak.py>
    
    cd iCULeak.py
    
    pip install -r requirements.txt

## 工具使用  

针对目标手机设备，运行iCULeak.py文件，并输入DNS域名空间中的主机名：

    
    
    python iCULeak.py -u domain\\llt4l -c 10.100.1.29 10.100.1.1

提供包含目标设备列表的文件来进行扫描：

    
    
    python iCULeak.py -l phones_hostnames -c 10.100.1.29 10.100.1.1

### 参数选项

1.使用“-h”或“--help”查看帮助页面；

2.使用“-u”或“--user”来传递ADIDNS验证用户名，形式为：domain\\\llt4l；

3.使用“-p”或“--password”来传递用户密码，如果你只传递了用户名而没有传递密码，工具将会在运行时弹出密码输入提示；

4.使用“-c”或“--cucm-server”选项来传递CUCM服务器的IP地址或主机名；

5.使用“-l”或“--list”标签来提供一份包含手机主机名的列表，其中的每一行类似：SEP112233445566；

6.如果你想要将分析结果存储为CSV文件，可以使用“-s”或“--save”标签，并输入想要保存的文件名称；

7.默认配置下，iCULeak.py会检测是否包含AD的有效凭证，我们可以使用“-nA”或“--no-authentication”来禁用该功能；

8.使用“-O”或“--out-dir”参数并加上目录名称，可以将所有的手机配置文件存储到一个目录中；

9.如需查看详细的分析过程日志，可以使用“-v”或“--verbose”参数来启用verbose模式；

## 项目地址

iCULeak：【[GitHub传送门](https://github.com/llt4l/iCULeak.py)】

***参考来源：[llt4l](https://github.com/llt4l/iCULeak.py)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

