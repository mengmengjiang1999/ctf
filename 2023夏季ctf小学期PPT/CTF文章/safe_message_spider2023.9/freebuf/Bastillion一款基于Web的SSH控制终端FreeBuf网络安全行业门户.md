![](https://image.3001.net/images/20201002/1601605734_5f769066f25ac87db05c9.png!small)

## Bastillion

Bastillion是一款基于Web的SSH控制终端，该工具可以帮助广大开发人员集中管理针对目标系统的管理员权限访问。这款基于Web的管理工具还结合了用户公共SSH密钥的管理和分发，而密钥的管理需要基于配置文件中定义的用户身份来进行分配。

管理员可以使用Authy或Google
Authenticator来在登录时开启双因素身份验证功能。登录后，他们就可以管理公共SSH密钥，或通过一个WebShell来连接到他们的系统中了。在Bastillion中，命令是可以跨Shell共享的，这样可以简化操作，并消除冗余的命令执行。

Bastillion将TLS/SSL层放在SSH之上，并充当bastion主机进行管理。由于Bastillion使用的协议栈为TLS/SSL+SSH，因此基础设施不能通过隧道/端口转发来暴露在外。另外，默认情况下启用SSH密钥管理，以防止非托管公钥并强制实施最佳实践。

![](https://image.3001.net/images/20201002/1601605745_5f76907188c5893e501ca.png!small)

## Bastillion下载

广大研究人员可以直接点击【[ _这里_](https://github.com/bastillion-io/Bastillion/releases)】来下载Bastillion的发布版本。

除此之外，我们也可以直接在AWS商城中获取Bastillion【[
_传送门_](https://aws.amazon.com/marketplace/pp/Loophole-LLC-Bastillion/B076PNFPCL)】。

当然了，由于Bastillion可以通过FreeBSD端口系统来在FreeBSD平台上进行安装，因此广大研究人员也可以通过下列命令来安装Bastillion：

    
    
    pkg install security/bastillion

## 依赖组件

安装并部署Open-JDK / Oracle-JDK v1.9或更高版本【[
_文档_](http://www.oracle.com/technetwork/java/javase/downloads/index.html)】：

    
    
    apt-get install openjdk-9-jdk

## 使用Jetty构建项目

首先，我们需要点击【[ _这里_](https://github.com/bastillion-io/Bastillion/releases)】下载bastillion-jetty-vXX.XX.tar.gz。接下来，我们需要导出环境变量。

### Linux/Unix/macOS：

    
    
    export JAVA_HOME=/path/to/jdk
    
     export PATH=$JAVA_HOME/bin:$PATH

### Windows：

    
    
    set JAVA_HOME=C:\path\to\jdk
    
     set PATH=%JAVA_HOME%\bin;%PATH%

接下来，我们就可以安装Bastillion了。

### Linux/Unix/macOS：

    
    
    ./startBastillion.sh

### Windows：

    
    
    startBastillion.bat

## 源码构建

首先，我们需要安装Maven3或更高版本：

    
    
    apt-get install maven

安装Loophole MVC：【[ _传送门_](https://github.com/bastillion-io/lmvc)】

### 导出环境变量：

    
    
    export JAVA_HOME=/path/to/jdk
    
    export M2_HOME=/path/to/maven
    
    export PATH=$JAVA_HOME/bin:$M2_HOME/bin:$PATH

切换到包含了pom.xml文件的目录中，然后运行下列命令：

    
    
    mvn package jetty:run

## 工具使用

打开你的浏览器，然后访问https://<whatever ip>:8443，并使用下列凭证登录：

    
    
    username:admin
    
    password:changeme

## 管理SSH密钥

默认配置下，Bastillion会针对目标系统重写authorized_keys文件中的所有配置值，我们也可以修改BastillionConfig.properties文件来禁用密钥管理功能，这样Bastillion就只会以Bastillion主机运行了，这个文件位于jetty/bastillion/WEB-INF/classes目录内：

    
    
    #set to false to disable key management. If false, the Bastillion public key will be appended to the authorized_keys file (instead of it being overwritten completely).
    
    keyManagementEnabled=false

除此之外，authorized_keys文件会根据应用程序的情况进行刷新，如果启用了密钥管理功能，那么我们就可以在BastillionConfig.properties文件中定义刷新间隔了：

    
    
    #authorized_keys refresh interval in minutes (no refresh for <=0)
    
    authKeysRefreshInterval=120

如果需要禁用或允许管理员设置任意公共密钥，可以按照如下代码编辑BastillionConfig.properties文件：

    
    
    #set to true to generate keys when added/managed by users and enforce strong passphrases set to false to allow users to set their own public key
    
    forceUserKeyGeneration=false

## 设置自定义SSH密钥对

我们还可以在BastillionConfig.properties文件中设置自定义的SSH密钥对：

    
    
    #set to true to regenerate and import SSH keys  --set to true
    
    resetApplicationSSHKey=true
    
     
    
    #SSH Key Type 'dsa' or 'rsa'
    
    sshKeyType=rsa
    
     
    
    #private key  --set pvt key
    
    privateKey=/Users/kavanagh/.ssh/id_rsa
    
     
    
    #public key  --set pub key
    
    publicKey=/Users/kavanagh/.ssh/id_rsa.pub
    
     
    
    #default passphrase  --leave blank if passphrase is empty
    
    defaultSSHPassphrase=myPa$$w0rd

## 调整数据库设置

我们还可以在配置选项中调整数据库设置：

    
    
    #Database user
    
    dbUser=bastillion
    
    #Database password
    
    dbPassword=p@$$w0rd!!
    
    #Database JDBC driver
    
    dbDriver=org.h2.Driver
    
    #Connection URL to the DB
    
    dbConnectionURL=jdbc:h2:keydb/bastillion;CIPHER=AES;

默认配置下，数据库是嵌入式的，但我们也可以通过调整连接URL来使用远程H2数据库：

    
    
    #Connection URL to the DB
    
    dbConnectionURL=jdbc:h2:tcp://<host>:<port>/~/bastillion;CIPHER=AES;

## 外部认证

我们还可以通过调整BastillionConfig.properties文件配置来启用外部认证：

    
    
    #specify a external authentication module (ex: ldap-ol, ldap-ad).  Edit the jaas.conf to set connection details
    
    jaasModule=ldap-ol

连接信息可以在jaas.conf文件中配置：

    
    
    ldap-ol {
    
    com.sun.security.auth.module.LdapLoginModule SUFFICIENT
    
    userProvider="ldap://hostname:389/ou=example,dc=bastillion,dc=com"
    
    userFilter="(&(uid={USERNAME})(objectClass=inetOrgPerson))"
    
    authzIdentity="{cn}"
    
    useSSL=false
    
    debug=false;
    
    };

通过使用org.eclipse.jetty.jaas.spi.LdapLoginModule，我们还可以映射和使用LDAP角色：

    
    
    ldap-ol-with-roles {
    
        //openldap auth with roles that can map to profiles
    
        org.eclipse.jetty.jaas.spi.LdapLoginModule required
    
        debug="false"
    
        useLdaps="false"
    
        contextFactory="com.sun.jndi.ldap.LdapCtxFactory"
    
        hostname="<SERVER>"
    
        port="389"
    
        bindDn="<BIND-DN>"
    
        bindPassword="<BIND-DN PASSWORD>"
    
        authenticationMethod="simple"
    
        forceBindingLogin="true"
    
        userBaseDn="ou=users,dc=bastillion,dc=com"
    
        userRdnAttribute="uid"
    
        userIdAttribute="uid"
    
        userPasswordAttribute="userPassword"
    
        userObjectClass="inetOrgPerson"
    
        roleBaseDn="ou=groups,dc=bastillion,dc=com"
    
        roleNameAttribute="cn"
    
        roleMemberAttribute="member"
    
        roleObjectClass="groupOfNames";
    
    };

## 工具使用截图

![](https://image.3001.net/images/20201002/1601606061_5f7691ad0a93b4b1e9af6.png!small)

![](https://image.3001.net/images/20201002/1601606068_5f7691b48cfadbd5ed030.png!small)

![](https://image.3001.net/images/20201002/1601606074_5f7691ba99b4167b6d3d4.png!small)

![](https://image.3001.net/images/20201002/1601606081_5f7691c1bceb6e7c5d0e7.png!small)

![](https://image.3001.net/images/20201002/1601606089_5f7691c98cea0f551d854.png!small)

![](https://image.3001.net/images/20201002/1601606097_5f7691d130d2f174b28f0.png!small)

![](https://image.3001.net/images/20201002/1601606105_5f7691d93e1abdaf3e3eb.png!small)

## 许可证协议

Bastillion的开发与发布遵循AGPL开源许可证协议。

## 项目地址

Bastillion：【[ _GitHub传送门_](https://github.com/bastillion-io/Bastillion)】

