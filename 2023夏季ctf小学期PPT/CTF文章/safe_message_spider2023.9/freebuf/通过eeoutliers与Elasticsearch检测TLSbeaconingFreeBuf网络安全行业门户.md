**ee-outliers 是用于检测存储在 Elasticsearch 中的事件的异常值的工具，这篇文章中将展示如何使用 ee-outliers
检测存储在 Elasticsearch 中的安全事件中的 TLS beaconing 连接。Beaconing
连接是定期发起的连接，可能表示计算机已经被感染在进行控制通信，例如从 C &C 服务器中获取指令或者静默地在网络中外传数据。**

![](https://image.3001.net/images/20190507/15572092191331.png!small)

## 预备 ee-outliers

ee-outliers 完全在 Docker 上运行，因此对环境的要求接近于零。唯一的要求是对 Docker 和 Elasticsearch
集群的连接配置，使其可以访问数据。

该项目的 GitHub 的[README](https://github.com/NVISO-BE/ee-outliers)页面已经包含了所有细节，无需赘述。

### 创建配置文件

GitHub 上 ee-outliers 的默认配置文件中包含了所需要的所有配置选项。首先修改 `general` 部分中的参数，确保 ee-outliers 可以连接到 Elasticsearch 集群。使用时可以保留所有默认值，包括 `beaconing_batch_eval_size`。

    
    
    [beaconing]
    # 在查找异常值前，需要同时定义处理多少事件
    # 事件数量的增多通常意味着会有更好的结果，但会导致内存使用量增加
    beaconing_batch_eval_size=1000000
    

将参数 `print_outliers_to_console` 设置为 1，就可以直接在命令行输出中看到检出的异常值，这便于进一步调试。

    
    
    print_outliers_to_console=1
    

额外需要调整一下 ee-outliers 的时间戳字段，提供一个 grok 模式将其转换为 `days, hours, minutes`
的形式，便于人类阅读。事件的时间戳字段为 `timestamp`，由此派生出的字段包括 `timestamp_day` 和
`timestamp_hour`。

    
    
    ##############################
    # DERIVED FIELDS
    ##############################
    [derivedfields]
    timestamp=%{YEAR:timestamp_year}-%{MONTHNUM:timestamp_month}-%{MONTHDAY:timestamp_day}[T ]%{HOUR:timestamp_hour}:?%{MINUTE:timestamp_minute}(?::?%{SECOND:timestamp_second})?%{ISO8601_TIMEZONE:timestamp_timezone}?
    

接下来增加一部分新配置，用于定义统计 TLS beaconing 的检测模型，此用例已在示例配置文件中定义过了，如下所示：

    
    
    ##############################
    # BEACONING - DETECT OUTBOUND SSL BEACONING - TLS
    ##############################
    [beaconing_ssl_outbound]
    es_query_filter=BroFilter.event_type:"ssl.log" AND _exists_:BroFilter.server_name
    
    aggregator=BroFilter.server_name,BroFilter.id_orig_h,timestamp_day
    target=timestamp_hour
    trigger_sensitivity=1
    
    outlier_type=suspicious connection
    outlier_reason=beaconing TLS connection
    outlier_summary=beaconing TLS connection to {BroFilter.server_name}
    
    run_model=1
    test_model=0
    

让我们逐行解释一下，方括号之间的部分是要运行的模型名，名字都以 `beaconing_` 为开头，这样 ee-outliers 就知道应用统计
beaconing 检测模型了。

    
    
    [beaconing_ssl_outbound]
    

参数 `es_query_filter` 指定模型要使用的 Elasticsearch 查询，便于收集要分析的事件。在这个特定场景下，从存储在集群中的
ssl.log 文件中选择所有 Bro（Zeek）事件。此外，要筛选出创建 server name 字段的 SSL 事件，稍后在 aggregator
中要使用到这个字段：

    
    
    es_query_filter=BroFilter.event_type:"ssl.log" AND _exists_:BroFilter.server_name
    

模型将为每个单独的 aggregator 字段计算目标字段的所有唯一实例。在这个特定场景下，这意味着 ee-outliers 为一天中的每小时都创建
`buckets`（前文创建的派生字段之一——`timestamp_hour`），并用 aggregator 的每个唯一实例组合填充这些
`buckets`。

    
    
    aggregator=BroFilter.server_name,BroFilter.id_orig_h,timestamp_day
    target=timestamp_hour
    trigger_sensitivity=1
    

例如，假设集群中关于域名 `sneaky.com` 的 TLS 连接事件每小时大约出现 5 次，都是针对特定源 IP
地址（192.168.0.2）和特定的日期（19/12）的。然后 ee-outliers 将会创建下列 `buckets` 来发现异常值：

    
    
    Aggregator: "sneaky.com - 192.168.0.2 - 19/12"
    Target: 00 (midnight)
    Total count: 5
    
    Aggregator: "sneaky.com - 192.168.0.2 - 19/12"
    Target: 01 (01:00 AM)
    Total count: 4
    
    Aggregator: "sneaky.com - 192.168.0.2 - 19/12"
    Target: 02 (02:00 AM)
    Total count: 5
    ...
    

aggregator 中所有可能的实例组合都会装进 `buckets` 中。在这个特定场景下就是 ee-outliers 处理事件范围内唯一 server
name、源 IP 地址与时间的组合。

触发灵敏度定义了允许存在多少“标准差”。在上面的例子中，凌晨 1 点只存在 4 个而不是 5
个请求，如果不容忍一些偏差的存在，就不会被视为异常！通过将触发灵敏度设置为 1 或者更高，将不会错过那些微小偏差的异常值。例如，在
`trigger_sensitivity` 设置为 1 的情况下，下面 24 个计数值（一天中每小时一个）都是 beaconing。

    
    
    5 5 5 4 4 5 5 5 5 3 5 5 5 2 5 5 5 5 4 5 5 5 5 5
    

标准差是 0.74，小于设置值 1，所以这个 24 个 `buckets` 的所有事件都会被标记为异常值。

此外，`beaconing` 模型的内置要求是至少需要 10 个 `buckets`，否则不会检测到 `beaconing`。换句话说，上面如果只有 9
个值而不是 24 个，或者不满足最少的 10 个值的任意个值都不会被标记为异常值。

然后指定异常值类型、成因和摘要。请注意，摘要中可以包含占位符字段，这些字段都会在异常事件中得到丰富，并且将使分析师更容易在以后对其进行可视化。

    
    
    outlier_type=suspicious connection
    outlier_reason=beaconing TLS connection
    outlier_summary=beaconing TLS connection to {BroFilter.server_name}
    

最后，让 ee-outliers 运行该模型。在配置文件的 `general` 部分中全局启用或禁用运行与测试的开关。

    
    
    run_model=1
    test_model=0
    

## 运行 ee-outliers

配置好模型后，运行 ee-outliers 来查看结果。按照 GitHub 上的 README 页面所述运行 ee-outliers。以交互模式运行时，我们可以在命令行输出中看到结果。按照需要，可能需要配置 Docker 网络使得 ee-outliers 能够访问
Elasticsearch，按照 README 页面配置即可，接下来称该网络为 `sensor_network`。

    
    
    # 构建镜像
    docker build -t "outliers-dev" .
    
    # 运行镜像
    docker run --network=sensor_network -v "$PWD/defaults:/mappedvolumes/config" -i outliers-dev:latest python3 outliers.py interactive --config /mappedvolumes/config/outliers.conf
    

查看输出，似乎已经发现了显示为 beaconing 行为的事件：

    
    
    2018-12-11 23:32:02 - INFO - ===== evaluating ssl_outbound outlier detection =====
    2018-12-11 23:32:02 - INFO - analyzing 6,001 events
    2018-12-11 23:32:05 - INFO - ssl_outbound - evaluating beaconing model [100.00% done]
    2018-12-11 23:32:05 - INFO - evaluating batch of 6,001 terms
    2018-12-11 23:32:05 - INFO - outlier - beaconing TLS connection to rules.emergingthreatspro.com
    2018-12-11 23:32:05 - INFO - outlier - beaconing TLS connection to rules.emergingthreatspro.com
    2018-12-11 23:32:05 - INFO - outlier - beaconing TLS connection to rules.emergingthreatspro.com
    2018-12-11 23:32:05 - INFO - outlier - beaconing TLS connection to rules.emergingthreatspro.com
    2018-12-11 23:32:05 - INFO - outlier - beaconing TLS connection to rules.emergingthreatspro.com
    2018-12-11 23:32:05 - INFO - outlier - beaconing TLS connection to rules.emergingthreatspro.com
    2018-12-11 23:32:05 - INFO - outlier - beaconing TLS connection to rules.emergingthreatspro.com
    

如果在配置文件中启用了 `es_save_results` 选项，这些事件会被在异常值字段中被标记，就可以对其进行可视化。

## 可视化结果

我们使用 Kibana 来可视化新标记的异常事件，基于包含 `outliers.reason`
的所有事件创建直方图。此外还创建了两个表来展示异常值类型与成因，分析师可以快速筛选出感兴趣的内容。

![](https://image.3001.net/images/20190507/15572094355146.png!small)

过滤 `beaconing TLS connection`（这是在之前定义的 `outlier_reason` 字段的名称），接下来创建一个过滤
`outlier_summary` 字段的表：

![](https://image.3001.net/images/20190507/15572094485104.png!small)

深入展示列表的第二个命中，再次进行过滤 `rules.emergingthreatspro.com` 就可以得到以下的直方图了。

![](https://image.3001.net/images/20190507/15572094577511.png!small)

看起来就像是 `beaconing` 行为，事实上这是我们实验室的设备，定期在 Emerging Threats 网站中提取新的 IDS 规则

通过检查 aggregator 的值，我们可以看到计算出了哪些 `buckets`（格式：server_name - IP -hour，与之前定义的完全一致）

![](https://image.3001.net/images/20190507/15572094658048.png!small)

最后下钻 `terms` 字段，可以看到每小时发出了多少请求。请注意，outliers 对每天都进行分析，因为 `timestamp_day` 是配置的
aggregator 字段的一部分

![](https://image.3001.net/images/20190507/15572094737823.png!small)

## 结论

在这篇文章中，展示了 ee-outliers 检测存储在 Elasticsearch 中的任意字段组合的 beaconing
行为的能力。`beaconing` 模型可以被用于更多场景：Windows 登录、HTTP 和 DNS beaconing
等。配置触发灵敏度可以决定模型以多严格的标准检测异常值，也为分析师提供根据需要调整和定制的能力。最后，通过使用新字段丰富每个异常事件，在任何喜欢的可视化工具中制作显示异常值的仪表板。

 ***参考来源：[nviso](https://blog.nviso.be/2018/12/11/tls-beaconing-detection-using-ee-outliers-and-elasticsearch/)，FB 小编 Avenger
编译，转载请注明来自FreeBuf（FreeBuf.COM）**

