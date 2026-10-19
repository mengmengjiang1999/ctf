包含crt.sh、fullhunt、fofa、360quake、fofa、hunter、virustotal、zoomeye的获取子域名的集成工具。

  * ## 说明

除crt.sh外，其他平台需要在config.ini中配置api。

下载地址：https://github.com/a1most/disu

  * ## 使用

工具可使用-f参数批量从文本文件中收集子域名，或使用-d参数直接指定单个待收集域名。在使用-f参数时，需制定-t参数来设置进程数。

![1663212396_63229b6c7bc2f7142ea4d.png!small](https://image.3001.net/images/20220915/1663212396_63229b6c7bc2f7142ea4d.png!small)

  * ### 单个域名获取

python3 disu.py -d baidu.com

在未配置api的情况：

[![1663206603508](https://image.3001.net/images/20220915/1663213336_63229f1817dce2d651625.png!small)](https://image.3001.net/images/20220915/1663213336_63229f1817dce2d651625.png!small)

正常配置情况如下：

###
[![image](https://image.3001.net/images/20220915/1663213339_63229f1bd7001138358cb.png!small)  
](https://image.3001.net/images/20220915/1663213339_63229f1bd7001138358cb.png!small)

  * ### 批量子域名获取

![1663212396_63229b6c7bc2f7142ea4d.png!small?1663212397636](https://image.3001.net/images/20220915/1663212396_63229b6c7bc2f7142ea4d.png!small?1663212397636)

最终生成的结果保存在output文件下面，按域名保存。

结果示例如下：

![1663212905_63229d69697b096c92727.png!small?1663212906514](https://image.3001.net/images/20220915/1663212905_63229d69697b096c92727.png!small?1663212906514)

  

