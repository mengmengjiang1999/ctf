URLFinder是一款用于快速提取检测页面中JS与URL的工具 。  
通常用于快速查找隐藏在页面或js中的敏感或未授权api接口 。

下载地址：<https://github.com/pingc0y/URLFinder>

## 功能说明

1.提取页面与JS中的JS及URL链接（页面URL最多深入一层，防止抓偏）  
2.提取到的链接会显示状态码、响应大小、标题等（带cookie操作时请使用-m 3 安全模式，防止误操作）  
3.支持配置Headers请求头  
4.支持提取批量URL  
5.支持结果导出到csv文件  
6.支持指定抓取域名  
7.记录抓取来源，便于手动分析

结果会优先显示输入的url顶级域名，其他域名不做区分显示在 other  
结果会优先显示200，按从小到大排序（输入的域名最优先，就算是404也会排序在其他子域名的200前面）

## 使用截图

单url截图（旧版截图）  
[![jagnp9.png](https://image.3001.net/images/20220926/1664187537_63317c9125a2bdc608906.png!small)](https://image.3001.net/images/20220926/1664187537_63317c9125a2bdc608906.png!small)  
批量url截图 （旧版截图）  
[![vRqHrd.png](https://image.3001.net/images/20220926/1664187540_63317c94510cd5b3f026f.png!small)](https://image.3001.net/images/20220926/1664187540_63317c94510cd5b3f026f.png!small)  
[![vRqbqA.png](https://image.3001.net/images/20220926/1664187543_63317c979380759408a60.png!small)](https://image.3001.net/images/20220926/1664187543_63317c979380759408a60.png!small)

## 使用

单url时使用

    
    
    URLFinder.exe -u http://www.baidu.com -s all -m 2
    URLFinder.exe -u http://www.baidu.com -s 200,403 -m 2
    

批量url时使用

    
    
    URLFinder.exe -s all -m 2 -f url.txt -o d:/
    

参数：

    
    
    -h  帮助信息 （可以看到当前版本更新日期）
    -u  目标URL
    -d  指定获取的域名
    -a  自定义user-agent请求头
    -s  显示指定状态码，all为显示全部
    -m  抓取模式：
            1  正常抓取（默认）
            2  深入抓取 （url只深入一层，防止抓偏）
            3  安全深入抓取（过滤delete，remove等敏感路由）
    -c  添加cookie
    -i  加载yaml配置文件（不存在时，会在当前目录创建一个默认yaml配置文件）
    -f  批量url抓取，需指定url文本路径
    -o  结果导出到csv文件，需指定导出文件目录（.代表当前目录）
    

