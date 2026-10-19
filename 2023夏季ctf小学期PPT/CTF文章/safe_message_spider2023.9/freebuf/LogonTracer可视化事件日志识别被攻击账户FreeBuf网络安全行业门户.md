## 前言

 **事件日志分析是安全事件调查中极其重要的一环。如果网络由Active
Directory管理（以下称为AD），则可以通过分析AD事件日志来识别。对于此类调查，直接在AD事件查看器中进行详细分析十分的困难;
常见的方法是将日志导出为文本格式或将其导入SIEM
/日志管理系统。但是，由于事件日志的数量、体积可能很大，导入时间受限于环境，这对分析师来说可能是一个难题。**

JPCERT开发并发布了一个支持此类事件日志分析的工具“LogonTracer”。本文介绍了它的工作原理以及如何使用。

## 事件日志可视化

LogonTracer将登录相关事件中的主机名（或IP地址）和帐户名关联起来，并将其可视化。这样，就可以看到哪个帐户尝试登陆以及登陆哪个主机。下图是LogonTracer创建的可视化图表，显示了一些IP地址和帐户的关系。

![事件日志可视化](https://image.3001.net/images/20181105/15413890946959.png!small)

对于每个节点，链接到主机（绿点）并带有一行账户信息（红/蓝）表示已使用主机登陆。

> 红色：SYSTEM权限帐户
>
> 蓝色：标准用户帐户
>
> 绿色：主机/ IP地址

即使对于一个没有详细了解过事件日志的新手，这种可视化也使日志分析变得简单。

## 提取更多重要帐户和主机

除了事件日志可视化之外，LogonTracer还能够通过排名显示可能的杠杆帐户/主机。图2是帐户和主机的重要性等级的示例。

![提取更多重要帐户和主机](https://image.3001.net/images/20181105/15413891195845.png!small)

对于此排名，LogonTracer会对事件日志图执行网络分析，并根据每个节点的“中心性”创建排名。中心性是指示每个节点与网络中心的接近度的索引。为了计算中心性，应用了PageRank
算法。在该算法中，与许多其他节点连接的节点位于图的中心，因此具有更高的中心性。

由于被攻击帐户用于对许多主机执行登录尝试，因此它们往往具有更高的中心性。因此，通过比较中心性，可以识别可能受影响的帐户/主机。

## 事件日志的时间顺序显示

使用LogonTracer，还可以按时间顺序显示事件日志。图3显示了时间序列中每个帐户的事件日志数。

![事件日志的时间顺序显示](https://image.3001.net/images/20181105/15413891424316.png!small)

通过检查一段时间内的日志数量，可以发现在短时间内或工作时间之外的未经授权的登录尝试。

事件日志的急剧增加会自动突出显示。为了检测异常登陆的计数增加，异常检测模式主要应用了变换查找器(详情可查看
<http://ieeexplore.ieee.org/document/1599387/>)。

## 如何安装LogonTracer

该工具可以在GitHub上找到。您可以从以下网页下载：

> JPCERTCC GitHub - LogonTracer
>
> <https://github.com/JPCERTCC/LogonTracer>

以下是有关如何使用LogonTracer的说明。该工具在Linux环境中进行了测试。

1\. 获取并安装Neo4j社区版

> 从以下网站下载Neo4j社区版并安装：
>
> <https://neo4j.com/download/other-releases/#releases>

2\. 下载LogonTracer

> 从以下网页下载并将其部署在一个文件夹中。
>
> <https://github.com/JPCERTCC/LogonTracer>

3\. 安装Neo4j JavaScript驱动程序

在LogonTracer的静态文件夹中安装Neo4j JavaScript驱动程序。

    
    
    $ cd LogonTracer/static
    
    $ npm install neo4j-driver

4\. 安装Python模块

为LogonTracer安装Python模块

    
    
    $ pip install -r requirements.txt

*如果statsmodels安装失败，请先安装numpy。

5\. 运行Neo4j

通过GUI或命令行启动Neo4j。

如何使用LogonTracer

使用以下选项启动LogonTracer：

    
    
    ```
    
    $ python3 logontracer.py -r -o [PORT] -u [USERNAME] -p [PASSWORD] -s [IP Address]
    
    ```
    
    
    - -r：启动Web服务器
    
    - -o：Web服务器运行的端口号（例如：8080）
    
    - -u：Neo4j用户名（默认为“neo4j”）
    
    - -p：Neo4j密码
    
    - -s：Web服务器运行的地址（例如：localhost）

下面是执行LogonTracer的示例。

![执行LogonTracer的示例](https://image.3001.net/images/20181105/15413892031159.png!small)

要访问Web界面，请从浏览器转到以下URL。（在此环境中，LogonTracer安装在本地环境中并在端口8080上运行）。

*要导入日志，您可以上传EVTX格式。

![上传EVTX格式](https://image.3001.net/images/20181105/15413892207818.png!small)

## 如何使用Docker镜像

Docker Hub上提供了LogOnTracer的Docker镜像。

<https://hub.docker.com/r/jpcertcc/docker-logontracer/>

如果使用Docker，可以通过以下命令启动映像：

    
    
    $ docker run \
    
    --detach \
    
    --publish=7474:7474 --publish=7687:7687 --publish=8080:8080 \
    
    -e LTHOSTNAME=[IP Address] \
    
    jpcertcc/docker-logontracer

LogonTracer可以分析的事件日志和注意事项

研究表明，监控以下事件对于调查未经授权的登录是有效的。基于此，LogonTracer还可以显示以下事件ID以进行可视化：

> 事件ID 4624：登录成功
>
> 事件ID 4625：登录失败
>
> 事件ID 4768：Kerberos身份验证（TGT请求）
>
> 事件ID 4769：Kerberos身份验证（ST请求）
>
> 事件ID 4776：NTLM身份验证
>
> 事件ID 4672：权限分配

由于并非所有上述事件ID都使用默认设置进行记录，因此需要启用审核策略以保留此类日志。我们建议启用审核策略。有关配置的详细说明，请参阅LogonTracer的“自述文件”，也可在GitHub上找到。

## 结语

虽然事件日志分析在事件调查中至关重要，但如果您不知道要分析什么以及从何处开始，则可能是一个耗时的过程。此工具通过可视化帐户和主机之间的关系提供简单的事件日志分析。我们希望您尝试使用此工具来准备实际事件调查。

我们将尽快更新有关如何使用此工具进行实际分析的更多信息。

谢谢你的阅读。

 ***本文作者：PikuYoake，转载请注明来自FreeBuf.COM**

