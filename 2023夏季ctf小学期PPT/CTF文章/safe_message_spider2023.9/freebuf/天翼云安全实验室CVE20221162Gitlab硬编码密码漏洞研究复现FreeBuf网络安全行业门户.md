# 漏洞原理

在Gitlab的某些版本中存在着 **通过硬编码的方式为Oauth登录的用户设置默认密码**
的漏洞。具体来说，如果自行搭建的Gitlab开启了Oauth登录如Github登录、Google登录等，Gitlab在为这些第三方登录的用户创建账户时，会使用
**硬编码** 的方式设置用户密码，导致这些用户的密码都一样，这样子就很危险啊。  
通过[修复commit](https://gitlab.com/gitlab-org/gitlab/-/commit/e2fb87ec5d4e235d6b83454980cec9c049849a1c#f4d654b98cc11d931e3f77ee61318adc95a52f12)可以看到，关于Gitlab上硬编码这一段漏洞源码大概是这样子：  
![硬编码生成默认密码](https://image.3001.net/images/20220412/1649745584_62551eb0870fe33e89dea.png!small)  
![为Oauth登录用户生成默认密码](https://image.3001.net/images/20220412/1649745612_62551eccc159e891aaeda.png!small)  
所以攻击者可以通过形似`123qweQWE!@#0000`的密码尝试登录Gitlab用户的帐号，默认密码的长度是21，因此也就是字符串`123qweQWE!@#000000000`。当然目前该漏洞已经得到了修复了，但受影响的漏洞版本却不会被历史遗忘，包括Gitlab-CE和Gitlab-CC的以下版本：

  * 14.7至14.7.6

  * 14.8至14.8.4

  * 14.9至14.9.1

# 环境搭建

环境分为两部分，首先是受影响范围内的Gitlab，其次需要构建用于Oauth的第三方登录。

## 搭建Gitlab

本文使用受影响的Gitlab-CE版本14.7.0，直接写个`docker-compose.yml`启动：

    
    
    version: '3'
    services:
      gitlab:
        image: 'gitlab/gitlab-ce:14.7.4-ce.0'
        container_name: 'gitlab'
        restart: always
        privileged: true
        hostname: 'gitlab'
        environment:
          TZ: 'Asia/Shanghai'
        ports:
          - '8080:80'
        volumes:
          - ./config:/etc/gitlab
          - ./data:/var/opt/gitlab
          - ./logs:/var/log/gitlab
    

创建好用于映射的3个目录，然后直接`docker-compose up -d`启动。

## Github App

Oauth第三方登录使用[Github App](https://github.com/settings/applications/new)，最主要的信息是
**callback URL** ，为github地址加上`/users/auth/github/callback`，github使用 **本地地址**
没有问题，我们只是改了下本地hosts给它个域名比较好看。  
![注册Github
App](https://image.3001.net/images/20220412/1649745640_62551ee823e3316795bfe.png!small)  
注册完成App之后就得到了 **ID** 和 **secrets** 。

## 配置Gitlab

修改Gitlab的配置文件`github.rb`以开启使用github作为第三方Oauth登录。

    
    
    ### OmniAuth Settings
    ###! Docs: https://docs.gitlab.com/ee/integration/omniauth.html
    gitlab_rails['omniauth_enabled'] = true   # 开启功能
    gitlab_rails['omniauth_allow_single_sign_on'] = ['github']   # 使用github登录
    gitlab_rails['omniauth_block_auto_created_users'] = false   # 自动创建用户帐号
    gitlab_rails['omniauth_auto_link_user'] = ['github']   # 链接github用户信息
    gitlab_rails['omniauth_providers'] = [   # 设置github第三方登录信息
      {"name" => "github",
       "app_id" => "APP_ID",
       "app_secret" => "APP_SECRET",
       "args" => {
         "scope" => "user:email"
       }
      }
    ]
    

然后重启docker镜像以开启配置。

    
    
    docker restart xxxx
    

# 漏洞验证

打开Gitlab就可以选择Github登录了，点击后跳转Github登录，登录回来后就新增了和Github用户同名的用户。  
![通过Github第三方登录Gitlab](https://image.3001.net/images/20220412/1649745661_62551efd33efb4fb4c7b9.png!small)  
完后退出登录，再使用该用户名与密码`123qweQWE!@#000000000`登录成功。  
![使用硬编码默认密码登录用户](https://image.3001.net/images/20220412/1649745681_62551f11472cd6e9362d5.png!small)

# 漏洞修复建议

由于官方已经对漏洞进行了修复，所以 **升级Gitlab** 到安全的版本肯定是最佳选择。  
其次对于可能已经存在该弱密码的用户，则需要提醒修改密码，但用户并不知道自己的密码是不是弱密码，所以最好 **提醒自己的Gitlab用户更新一次登录密码**
。

# 参考

  * [CVE-2022-1162](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-1162)

  * [Gitlab对该漏洞进行修复的commit](https://gitlab.com/gitlab-org/gitlab/-/commit/e2fb87ec5d4e235d6b83454980cec9c049849a1c#f4d654b98cc11d931e3f77ee61318adc95a52f12)

  * [GitLab Releases Patch for Critical Vulnerability That Could Let Attackers Hijack Accounts](https://thehackernews.com/2022/04/gitlab-releases-patch-for-critical.html)

  * <https://securityonline.info/cve-2022-1162-gitlab-vulnerability/>

