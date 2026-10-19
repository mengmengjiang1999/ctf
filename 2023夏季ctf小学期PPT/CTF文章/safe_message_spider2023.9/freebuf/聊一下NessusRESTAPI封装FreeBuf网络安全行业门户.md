## 前言

Nessus 作为主机扫描的一款经典工具，功能比较丰富，工具本身就不多做介绍了。

我们希望能将 Nessus Scanner 节点进行封装，作为自研扫描调度系统中的一类扫描节点，作为基础例行安全扫描。

Github : <https://github.com/starnightcyber/nessus_api>  

此外，官方已有封装(Nessus 6)：https://github.com/tenable/nessrest，但这个已经比较陈旧了。

## 准备工作

### Nessus 环境搭建

简单介绍下环境搭建部分，我们使用前人已经搭好的 Docker 镜像 **leishianquan/awvs-nessus** ，致敬。

    
    
    # docker search awvs
    NAME                          DESCRIPTION                                     STARS               OFFICIAL            AUTOMATED
    secfa/docker-awvs             AWVS 14.6.211220100  Linux Version Crack By …   74                                      
    **leishianquan/awvs-nessus** 25   
    ...
    
    
    # 拉取镜像
    docker pull leishianquan/awvs-nessus:v1
    # 启动
    docker run -it -d -p 13443:3443 -p 8834:8834 leishianquan/awvs-nessus:v1
    # 查看容器
    docker ps –a
    # 启动容器
    docker start container-id
    # 进入容器
    docker exec –it container-id /bin/bash
    # 进入容器后，启动nessus
    /etc/init.d/nessusd start
    # 访问扫描器地址和账号密码
    Nessus:
    https://127.0.0.1:8834/#/
    account:leishi/leishianquan
    Awvs13:
    https://127.0.0.1:13443/
    account:admin@admin.com/Admin123

Note: awvs-nessus镜像比较大，9.01GB，请自行解决。

修改默认密码，请参考 <https://www.cnblogs.com/Hi-blog/p/Nessus-AWVS-Docker.html>  

### Nessus REST API AK/SK 生成

安装启动，登录之后，点击右上角图标 >> My Account >> API Keys，或者直接访问如下链接：

[https://127.0.0.1:8834/#/settings/my-account/api-keys](https://106.3.140.250:8834/#/settings/my-account/api-keys)  

点击 Generate >>

![](https://image.3001.net/images/20220212/1644637891_62072ec3b85ebd35b681f.png!small)

Note:保存好该 AK/SK（64位），只会展示一次，eg.

    
    
    ak = '91f4e8d70e828f63df0d2d9c0c593f19e0e6f5f5406b88cc4f5be9a53fd4f572'
    sk = '0b78e392b54f4847ba91a95833f09b308ad7018f1f34556923de46e16aa7baf1'

后续就只使用该 AK/SK，不会使用 Nessus console 登录的用户名密码。

##  **Nessus REST API Doc**

安装好 Nessus 扫描器之后，会自带 API
文档，[https://127.0.0.1:8834/api#/overview](https://106.3.140.250:8834/api#/overview)  

### Resource Type

所有资源类型如下：

    
    
    agent-groups
    agents
    editor
    file
    folders
    groups
    mail
    migration
    permissions
    plugin-rules
    plugins
    policies
    proxy
    scanners
    scans
    server
    session
    settings
    software-update
    tokens
    users

我们不会封装所有的接口，只需要封装其中一部分即可达成我们的需求，而且有些操作的参数较多，具体可以查看上述文档链接。

后面会介绍如何自己动手去封装所需的操作。

### AK/SK 使用示例

认证授权
[https://127.0.0.1:8834/api#/authorization](https://106.3.140.250:8834/api#/authorization)  

需要设置 HTTP 请求头 X-ApiKeys，填充 AK/SK 信息

    
    
    X-ApiKeys: accessKey={accessKey}; secretKey={secretKey};

curl 示例说明

    
    
    curl -H "X-ApiKeys: accessKey={accessKey}; secretKey={secretKey}" https://localhost:8834/scans

获取 folders 信息示例

    
    
    curl -k -H "X-ApiKeys: accessKey=91f4e8d70e828f63df0d2d9c0c593f19e0e6f5f5406b88cc4f5be9a53fd4f572; secretKey=0b78e392b54f4847ba91a95833f09b308ad7018f1f34556923de46e16aa7baf1" https://127.0.0.1:8834/folders | python -m json.tool
    {
        "folders": [
            {
                "custom": 0,
                "default_tag": 0,
                "id": 6,
                "name": "Trash",
                "type": "trash",
                "unread_count": null
            },
            {
                "custom": 0,
                "default_tag": 1,
                "id": 7,
                "name": "My Scans",
                "type": "main",
                "unread_count": 13
            }
        ]
    }

## REST API 封装

到这里我们可以尝试自己封装一下 Nessus REST API 提供的操作，以创建一个扫描任务，这里可以借助我们的好伙伴
BurpSuite，可以让我们更直观的查看需要设置的参数。

我们在 Nessus console 操作，使用自定义扫描策略，创建一个扫描任务。

![1644634617_620721f906dafa5b07083.png!small?1644634616996](https://image.3001.net/images/20220212/1644634617_620721f906dafa5b07083.png!small?1644634616996)

同时对照着官方文档说明，封装对应的功能操作，
[https://127.0.0.1:8834/api#/resources/scans/create](https://106.3.140.250:8834/api#/resources/scans/create)  

    
    
    def create_scan(self, targets, name='nessus scan', description='nessus', folder_id='', policy_id='8'):  
    '''  
    创建扫描任务，需至少填充扫描策略参数，建议备注清楚 name 及其它参数  
    Create a scan, must set policy_id parameter to specify the scan policy  
    :param targets: scan target ips  
    :param name: scan task name  
    :param description: scan task description  
    :param folder_id: put the task to folder_id  
    :param policy_id: using which scan policy  
    :return: None  
    '''  
    print('[*] create_scan ...')  
    # POST /scans  
    url = '{}/{}'.format(self.url, 'scans')  
    # print('url => {}'.format(url))  
    # nesssus 创建任务时，使用 burpsuite 抓个包，就是需要填充的数据字段  
    data = {  
    "uuid": "ad629e16-03b6-8c1d-cef6-ef8c9dd3c658d24bd260ef5f9e66",  
    "settings": {  
     # "emails": "",  
     # "filter_type": "and",  
     # "filters": [],  
     "launch_now": 'true',      # 是否立即执行，设置为 true 则直接执行，否则只创建任务  
     "name": name,  
     "description": description,  
     "folder_id": folder_id,     # 没有设置 folder_id, 则在 All Scans 可以看到  
     "scanner_id": "1",  
     "policy_id": policy_id,  
     "text_targets": targets,  
     # "file_targets": ""  
    }  
    }  
    try:  
    resp = requests.post(url=url, headers=self.headers,  
                      data=json.dumps(data, ensure_ascii=False).encode("utf-8"), verify=False)  
    if resp.status_code == 200:  
     # print(json.dumps(json.loads(resp.content), indent=4, ensure_ascii=False))  
     # 创建扫描任务成功，输出 scan_id 和 uuid  
     scan_id = json.loads(resp.content)['scan']['id']  
     uuid = json.loads(resp.content)['scan']['uuid']  
     print('[+] Scan [No.{}] -- {} created succeed ...'.format(scan_id, uuid))  
    else:  
     print(str(resp.content))  
    except Exception as e:  
    print(str(e))

不是所有参数都是必要提供的，可以略去一部分非必要参数。为保持完整，代码中仍然保留了。

## 已封装的功能

目前已封装如下基本操作，能完成当前所需功能，大家可以根据自身需求进一步封装和二次封装。

函数| 说明  
---|---  
`show`| 展示当前 nessus scanner 节点、扫描策略、目录和扫描任务信息  
`gen_random_str`| 生成随机小写字符和数字组合的字符串，默认 6 位  
`list_folders`| 列出当前 nessus scanner 的扫描目录  
`create_folder`| 创建目录  
`delete_folder`| 删除目录  
`clear_all_folders`| 删除所有目录  
`get_scanners`| 获取 nessus scanner 节点信息  
`get_scan_policies`| 获取自定义扫描策略  
`create_scan`| 创建扫描任务  
`launch_scan`| 启动扫描任务  
`launch_all_scan`| 启动所有扫描任务  
`get_scan_detail`| 获取扫描任务详细信息  
`get_all_scans`| 获取所有扫描任务信息  
`stop_scan`| 停止扫描任务  
`delete_scan`| 删除扫描任务  
`clear_all_scans`| 清理/删除所有扫描任务  
`export_scan_result`| 导出扫描任务结果  
`export_all_scan_results`| 导出所有扫描任务结果  
`clear_all`| 清楚所有自定义目录和扫描任务  
  
## 使用示例

大家可以使用示例 <https://github.com/starnightcyber/nessus_api/blob/main/sample.py>  

![1644636371_620728d336f256c243839.png!small?1644636371471](https://image.3001.net/images/20220212/1644636371_620728d336f256c243839.png!small?1644636371471)

## Further

  * 这里相当于是单个 Nessus 扫描节点，可实现一个类似于 Nessus Manager 的调度功能，来集中展示当期所有 Nessus 扫描节点的情况，根据任务负载更灵活调度。
  * 获取的扫描报告结果，可按漏洞等级进行数据展示，以及报告的中文翻译。

感兴趣的朋友可以一起封装一下，进一步完善，可 PR。

## MISC

Nessus REST API 封装：

<https://github.com/starnightcyber/nessus_api>  

个人收藏集合（值得一看）：

<https://github.com/starnightcyber/Miscellaneous>  

Nessus 报告转中文：

  * 中文漏洞库：<https://github.com/FunnyKun/NessusReportInChinese>  

  * py2 : <https://github.com/Bypass007/Nessus_to_report>  

  * py3 : <https://github.com/starnightcyber/Nessus_to_report>  

欢迎 star，谢谢 ~ :)

