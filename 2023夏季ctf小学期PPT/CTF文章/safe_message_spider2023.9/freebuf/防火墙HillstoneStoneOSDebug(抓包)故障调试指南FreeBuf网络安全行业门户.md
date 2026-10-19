## 1、Debug抓包说明  

⇒
Debug抓包前请务必查看设备CPU情况，如当前CPU偏高（参考值：≥50%），请谨慎进行抓包操作，最好选择在当前设备CPU值偏低、业务低峰期进行Debug，查看设备CPU具体命令：SG-6000#
show cpu detail (含历史CPU)。

⇒ Debug抓包后请务必关闭设备所有已开启的Debug，防止影响设备CPU等运行情况，关闭Debug方式：

① 命令行下：SG-6000# undebug all。

② 命令行下：长按或者按2下“Esc”键，提示 “The debug function for all modules is disabled”
表示所有已开启的 debug 均已关闭。

StoneOS 数据包(DP) Debug ⇓  
IP sec Debug ⇓  
其他类型 Debug ⇓  
系统调试功能可以帮助用户对错误进行诊断和定位。安全网关的各种协议和功能基本上都具有相应的调试功能。默认情况下，所有协议和功能的系统调试功能都是关闭的。用户只可以通过设备命令行对系统调试功能进行配置。  
Debug 操作有一定风险，尤其是设备流量大的时候开启 debug 会导致 CPU 高，请谨慎操作。 请在山石工程师的指导下操作， 不建议用户直接使用
debug。  
此文中 StoneOS 默认指防火墙。  

## 2\. 常见Debug抓包流程  

（一）数据包(DP) Debug 抓包流程  
a. Debug抓包前建议先了解下StoneOS数据包基础转发流程(非二层)：

图注一：StoneOS数据包基础转发流程图(非二层)

b. StoneOS数据包基础转发流程(非二层)具体如下：  
识别数据包的逻辑入接口，可能是一般无标签接口，也可能是子接口。从而确定数据包的源安全域。  
StoneOS 对数据包进行合法性检查。如果源安全域配置了攻击防护功能，系统会在这一步同时进行攻击防护功能检查。  
会话查询。如果该数据包属于某个已建立会话，则跳过 4 到 10，直接进行第 11 步。  
目的 NAT（DNAT）操作。如果能够查找到相匹配的 DNAT 规则，则为包做 DNAT 标记。因为路由查询需要 DNAT 转换的 IP 地址，所以先进行
DNAT 操作。  
*如果系统配置静态一对一BNAT规则，那么先查找匹配的BNAT规则。数据包匹配了BNAT规则之后，按照 BNAT 的设定进行处理，不再查找普通的 DNAT 规则。  
路由查询。 StoneOS 的路由查询顺序从前到后依次为：策略路由（PBR） >源接口路由（SIBR） >源路由（SBR） >目的路由（DBR） >ISP
路由。  
此时，系统得到了数据包的逻辑出接口和目的安全域。  
源 NAT（SNAT）操作。如果能够查找到相匹配的 SNAT 规则，则为包做 SNAT 标记。 *如果系统配置静态一对一 BNAT 规则，那么先查找匹配的
BNAT 规则。 数据包匹配了 BNAT规则之后，按照 BNAT 的设定进行处理，不再查找普通的 DNAT 规则。  
下一跳 VR 查询。如果下一跳为 VR，则继续查看指定的下一跳 VR 是否超出最大 VR 数限制（当前版本系统仅允许数据包最多通过 3 个
VR），如果超过则丢弃数据包，如果未超过，返回 4；如果下一跳不是 VR，则继续进行下一步策略查询。  
安全策略查询。系统根据数据包的源安全域、目的安全域、源 IP 地址和端口号、目的 IP
地址和端口号以及协议，查找策略规则。如果找不到匹配的策略规则，则丢弃数据包；如果找到匹配的策略规则，则根据规则指定的行为进行处理，分别是：  
· 允许（Permit）：允许数据包通过。  
· 拒绝（Deny）：拒绝数据包通过。  
· 隧道（Tunnel）：将数据包转发到指定的隧道。  
· 是否来自隧道（Fromtunnel）：检查数据包是否来自指定的隧道，如果是，则允许通过，如果不是，则丢弃。  
· Web 认证（WebAuth）： 对符合条件的流量进行 Web 认证。  
第一次应用类型识别。系统根据策略规则中配置的端口号和服务，尝试识别应用类型。  
会话建立。  
如果需要，进行第二次应用类型识别。根据数据包的内容和流量行为再次对应用类型进行精确识别。  
应用层行为控制。根据确定的应用类型，系统将在此执行配置的 Profile 和 ALG 功能。  
根据会话中记录的信息，例如 NAT 标记等，执行相应的处理操作。  
将数据包转发到出接口。  
c. 举例说明：

图注二：StoneOS实际Debug数据包转发流程（一）

图注三：StoneOS实际Debug数据包转发流程（二）

Top⇑

d. Debug操作步骤  
【以下红色粗体部分为一般debug操作步骤(必须)】

SG-6000# show cpu detail //查看设备当前CPU情况（如偏高，不建议debug）

SG-6000(config)# logging debug on //打开 debug log

SG-6000(config)# logging debug to buffer //记录 log 到 buffer

SG-6000(config)# no logging debug to console //不记录 log 到 console

SG-6000# debug dp filter src-ip x.x.x.x src-port xx dst-ip x.x.x.x dst-port xx
proto xxx //设置debug过滤条件 源IP 源端口 目的IP 目的端口 协议（可任选其中一项或多项作为debug过滤条件）

注：关于debug过滤条件说明，如果调试过程中需要查看双向数据包，即来回数据包转发情况，需要设置两条debug过滤条件，如常见情况第一条源目地址、端口为发送数据包方向，第二条源目地址、端口反过来写即为反向数据包(回包)，当然特殊情况下请以实际环境问题为准。

例一：抓ICMP 协议ping包 SG-6000# debug dp filter src-ip 192.168.1.1 dst-ip
192.168.100.233 proto icmp //抓包内容限制源目地址、协议  
例二：只抓ip地址报文 SG-6000# debug dp filter dst-ip 192.168.100.233 )

SG-6000# show dp filter 或 show dp-filter
//查看已设置的debug过滤条件（建议设置完过滤条件后，即查看已设置过滤条件，防止因debug过滤条件误设导致抓包出错）

SG-6000# undebug dp filter id xx //清除已设置的debug过滤条件

SG-6000# debug dp basic //debug
开关，查看数据包基本处理流程（务必先执行第一条过滤命令，否则debug所有数据包会造成CPU高或卡死）

SG-6000# debug dp snoop //查看StoneOS数据层转发基本信息（该功能可以看到数据包头部的信息，比如TCP
头部SYN/ACK/FIN/RST 等标志，序列号，二层MAC 地址等等。）

SG-6000# debug dp drop //查看StoneOS数据层丢弃基本信息

SG-6000# debug dp error //查看StoneOS错误的数据包

SG-6000# debug self //查看StoneOS自身数据包转发情况

SG-6000# show debug
//查看已开启的debug功能（建议设置完debug功能后，即查看已开启的debug功能，防止因debug功能误设导致抓包出错）

SG-6000# clear logging debug //清除debug缓存

清除debug缓存后，立马进行故障节点访问，即触发数据流，以便在防火墙抓取相应数据包转发信息（若防火墙抓不到相应数据包，如提示“Info: There is
no logging message”，则表示相应流量可能没到达防火墙，或者debug过滤条件、功能开关有误，请以实际情况为准，并进行检查）

SG-6000# show logging debug //查看debug输出信息，即StoneOS数据包转发情况

SG-6000# show logging debug | {include|begin|begin2|exclude|redirect}
Packet/Drop/RST/err等 //可通过管道符“|”来过滤目标信息，如“SG-6000#show logging debug | include
Packet”可直接查看数据包来回转发情况。

注：如需要记录相应debug输出信息，请使用带有“记录日志”功能的命令软件，具体请参考其软件使用说明。

SG-6000# undebug all //抓包完毕，关闭debug功能（长按或者按2下“Esc”键也可）

注意：使用Debug请注意设备CPU使用情况和所抓取报文的数据量，不可以在没有过滤条件的情况下进行Debug。

e. 常见Debug故障调试信息示例(StoneOS数据包)  
① “No policy matches, default ===DENY===”  
没有能匹配上的策略，需要确认策略配置是否正常。  
“policy id xx matches: ===DENY===”  
匹配上了拒绝策略，需要确认策略配置是否正常。

② “Policy xx matches, ===OUTTUNNEL===  
Dropped: Can't find policy/policy denied. Abort!!”  
匹配上 策略，但走了错误的隧道，需要检查是否开启了 check-id。

③ “flow0's tunnel id (0) invalid.  
Dropped: Failed to create session”  
需要检查 IP sec配置，常见原因为隧道接口绑定 IP sec 实例时配置的网关与路由配置的网关不一致（或一个配置了另一个未配置）。

④ “The to-self service is not registered”  
不应该发到防火墙自身的报文被 drop，需要确认配置是否正常（例如 DNAT 没有成功匹配等）。

⑤ “Chash insert fail  
Failed to install the following session”  
会话冲突导致会话创建失败，建议查询已有会话 flow 看是否存在冲突情况， 常见原因如需要创建会话的 flow0 和已有会话的 flow1 相同， zone
也相同时，就会冲突。

⑥ “Dropped: Arp get fail”  
ARP 信息获取失败，需要进一步排查 ARP 报文的收发情况，可能需结合镜像抓包等方式排查。如果显示的是 Arp get fail,
ip:0.0.0.0，说明可能是由于同一应用不同端口设备收到报文的源 MAC 不同等原因，需要重新请求
ARP，而接口又关闭了逆向路由导致，可尝试开启逆向路由测试。

⑦ “Dropped: Dst mac is not interface's mac, drop packet”  
目的 MAC 非接口 MAC 而被 drop，需要先确认报文是否为相关报文。如果是，那么需要排查上联设备的 ARP 学习情况，本端视情况可开启免费 ARP
再测试。

⑧ “Dropped: Address spoof detected!!  
Dropped: No reverse route, drop the packet”  
字面意思为检测到地址欺骗 drop 报文，常见于查询逆向路由时查找到的回包出接口与正向报文入接口不在同一安全域，此时 debug
就会看到这样的信息。需要检查配置文件确认路由配置是否正常。一般关闭逆向路由可规避，但关闭逆向路由可能造成其他问题，需要结合用户实际需求给出最优建议。  
“Get the reverse route: out interface's zone is not the zone of i_if of
packet,drop the packet  
Dropped: No reverse route, drop the packet”  
此 debug 信息与上面类似，常见原因大体相同，需要检查配置文件。

⑨ “Hit invalid session, drop packet”  
报文五元组命中了被拆除的会话被 drop，通常是由于之前有会话被拆除后还未经过 3 秒老化时间。

⑩ “Dropped: TCP 1st packet should not be RST or FIN”  
TCP 首包不能为 RST 或 FIN 包，关闭相关检查可以规避。

⑪ “There is not enough resource  
Dropped: SNAT error, dropped”  
SNAT 资源不足，需要检查 SNAT 资源状态，对于开启了端口扩展的情况，需要确认是否有pool 资源已用完。

⑫ “Dropped: The interface of dst mac is same as the src if”  
目的 MAC 对应的出接口与入接口一致，一般发生在透明模式环境中，设备认为该报文不应该被转发到设备因此丢弃，需要结合客户拓扑看是否正常。

⑬ “Received unreachable embedded icmp, invalidate sesstion”  
设备接收到 ICMP 不可达报文并拆除了会话，可能导致后续业务报文被 drop，配置 icmpunreachable-session-keep 可规避。

⑭ “Dropped: TTL is too small”  
TTL 过低，可能是设备收到报文的 TTL 就已经是 1，也可能是存在环路，需要结合拓扑及完整 debug 分析。

⑮ “iQoS process: QoS engine first pipe xxx（管道名） enqueue pak failed, drop it”  
报文被 iQoS 阻断。

⑯ “block pak for session xxxx（session ID） new app-id xxx（应用名）”  
由于应用识别功能识别出流量实际应用，应用发生变化， session rematch 时匹配到拒绝策略/默认拒绝动作导致报文被 drop。

更多其他类型的debug抓包详细操作步骤和注意事项请见：

[山石网科知识库](https://kb.hillstonenet.com/cn/stoneos-debug-troubleshooting-manual/)

