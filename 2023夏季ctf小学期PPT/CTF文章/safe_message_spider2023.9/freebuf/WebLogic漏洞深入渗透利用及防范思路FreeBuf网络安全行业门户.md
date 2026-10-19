**在《[关于WebLogic安全性探讨](https://www.freebuf.com/column/199624.html)》和《[WebLogic
XMLDecoder
漏洞分析](https://www.freebuf.com/column/207849.html)[](https://www.freebuf.com/column/207849.html)》等文章中都很详细的讲解了Weblogic存在的漏洞、利用方法以及修补措施。但是也只是停留在漏洞利用的角度来对其进行了分析，接下来我会对weblogic漏洞深入渗透利用提出几点思路，根据这几点思路大家可以对自己部署weblogic的服务器进行深入的检查。**

##  一、Weblogic密码破解

Weblogic中的登录密码会以密文的形式存储在服务器本地，当攻击者已经获得服务器权限后可以直接访问该文件。

> 文件名为：config.xml
>
> 文件路径为：./config/config.xml
    
    
    ...
    <node-manager-username>weblogic</node-manager-username> 
      <node-manager-password-encrypted>{AES}rCKfW/HFK7glAWw64jX5Uf2K9Nwz1mzL0f/4aE9uyt=</node-manager-password-encrypted> 
    ...

在config文件中的node-manager-username节点记录了webogic用户名，node-manager-password节点记录了密码，其加密方式为AES.

除了在config文件中找到用户名和密码外，在./servers/AdminServer/security/boot.properties文件中用户名和密码都会以密文的形式存储。

获取密文后需要对加密后的密码进行解密，解密文件位于./security/SerializedSystemIni.dat

针对如何破解weblogic密码，可参考[此文](https://my.oschina.net/u/351612/blog/758290)，破解过程中需要注意密文格式问题。

**防护方式：**

> 1、针对访问日志进行筛查，找到可疑IP地址
>
> 2、查看weblogic登录记录，是否有非法IP登录

##  二、稳定后门部署方式

Weblogic漏洞利用方式有以下几种：

> 1、利用漏洞上传小马、大马，对服务器进行控制，这种方式是现有文章中最常用的方法，此种方法是最容易发现清除的。
>
> 2、利用weblogic上的服务进行稳定控制，weblogic上常常会部署其他的业务，可根据不同业务的特点部署，例如网站服务等。
>
> 3、上传恶意软件对服务器进行控制，恶意软件通常会采用主动回连的方式进行通信。

**防护方式：**

> 1、对Weblogic下文件夹中的不明内容进行清除，木马文件会有很明显的特征
>
> 2、筛查服务器上所有服务中是否存在可疑文件
>
> 3、检查服务器上端口开放情况，网络连接情况。特别是大端口和常用端口。
>
> 4、根据文件修改时间筛查最新修改文件

##  三、后台服务渗透

weblogic后台常会有数据库连接，攻击者也会利用木马尝试连接内网中的数据库。

> 文件名为：jdbc.xml
>
> 文件路径为：./config/jdbc/jdbc.xml

该文件夹内会有后台数据库的连接信息，例如数据库类型，连接方式，用户名和密码等等。

示例：

    
    
     <jdbc-driver-params>
        <url>jdbc:oracle:thin:@//192.168.120.156:1521/ORCL</url>
        <driver-name>oracle.jdbc.xa.client.OracleXADataSource</driver-name>
        <properties>
          <property>
            <name>user</name>
            <value>kzbigix</value>
          </property>
        </properties>
        <password-encrypted>{AES}mjwf4r94FDUh/UfaakINte5mMUYEX8LMKAkyTEtyusw=</password-encrypted>
      </jdbc-driver-params>

密码破解方式同前文所述。防范方式也基本与前文所述相同。

##  四、其他姿势

还有各式各样的内网渗透姿势，例如端口转发：将内网3389端口利用端口转发工具映射到外网端口，攻击者就可以直接远程桌面登录；或者是直接用工具扫描内网机器漏洞，一般内网机器漏洞修补不及时就会造成很严重的影响。

以上也只是我自己的一些思路想法（不妥之处请温柔评论），请各位大佬能够提出更多思路以方便我们对服务器防护做的更全面。

 ***本文原创作者：Kriston，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

