## 评测背景

源代码属于企业核心资产，很多开发不经意间就会把他们的劳动成果分享出去，这种 “开源精神” 往往会给企业带来严重的安全风险，从而造成重大损失。

因此，构建代码泄露监控体系非常必要，此次我们花了不少时间对主流开源的代码泄露监控项目做了深度横向评测，以供大家参考。

项目| 地址| 出品方  
---|---|---  
GSIL| https://github.com/FeeiCN/GSIL| FEEI（阿里巴巴）  
Hawkeye| https://github.com/0xbug/Hawkeye| 0xbug  
码小六| https://github.com/4x99/code6| 4399  
Github-Monitor| https://github.com/VKSRC/Github-Monitor| VIPKID  
Github leaked patrol| https://github.com/MiSecurity/x-patrol| 小米  
  
* * *

## 项目活跃度

项目| 仓库创建时间| 活跃度| 问题响应速度  
---|---|---|---  
GSIL| 2017.10| 低| 慢  
Hawkeye| 2017.06| 中| 已关闭 Issues 功能，无法提交问题  
码小六| 2020.03| 高| 响应及时  
Github-Monitor| 2018.06| 低| 响应时间一般  
Github leaked patrol| 2018.02| 低| 几乎不响应  
  
所有项目均已发布 > 1 年，可能是小众项目且历时数年，大多数项目活跃度低，甚至个别项目有弃坑迹象，请谨慎选择！

* * *

## 安装部署

项目| 开发语言| 数据库| 源码部署| Docker 部署| 部署文档  
---|---|---|---|---|---  
GSIL| Python| ✕| ✓| ✕| ✓  
Hawkeye| Python| MongoDB| ?| ✓| 无源码部署文档  
码小六| PHP| MySQL| ✓| ✓| ✓  
Github-Monitor| Python| Redis| ✓| ✓| ✓  
Github leaked patrol| Go| SQLite3 / MySQL / PostgreSQL| ✓| ✕| ✕  
  
### 源码部署

Python 项目得注意用 2.x 还是 3.x 版本，可能会碰到各种依赖问题。码小六使用 PHP + Laravel，源码部署时有点麻烦。Github
leaked patrol 无任何部署文档且 Go 依赖错误，编译失败，无法参加后续评测。

### Docker 部署

Hawkeye 和码小六部署比较顺利，Github-Monitor 有个 pip 版本问题会导致启动失败，有多人提 Issue，但至今仍未修复。

* * *

## 界面交互

项目| 前端框架| 界面交互| 点评  
---|---|---|---  
GSIL| ✕| ✕| 无 UI 界面  
Hawkeye| Element| 较好| 有一些细节问题  
码小六| ExtJS / Vant（移动端）| 较好| ExtJS 较为小众  
Github-Monitor| Ant Design Pro| 中等| 扫描结果较多时显示不佳  
Github leaked patrol| AdminLTE| -| 无法运行  
  
此次评测的项目应该都没有产品 & 交互参与，或多或少都有一些设计及交互上的小问题，好在都用了成熟的前端框架，使用基本流畅。GitHub-Monitor
默认显示了代码片段，当扫描结果较多时，不方便查看。

### Hawkeye 界面

![Hawkeye](https://image.3001.net/images/20210608/1623114874_60bec47a6dc0dd51b8918.png!small)

### 码小六界面

![码小六](https://image.3001.net/images/20210608/1623114895_60bec48f63a3e0189d031.png!small)

![码小六](https://image.3001.net/images/20210608/1623114908_60bec49c6719c5546659b.png!small)

![码小六](https://image.3001.net/images/20210608/1623114916_60bec4a42f47af584c4ba.png!small)

### Github-Monitor 界面

![Github-Monitor](https://image.3001.net/images/20210608/1623114928_60bec4b0729d6b03cf924.jpg!small)

![Github-Monitor](https://image.3001.net/images/20210608/1623114938_60bec4ba0cb0e5c5c6576.jpg!small)

![Github-Monitor](https://image.3001.net/images/20210608/1623114948_60bec4c4412965d18e440.jpg!small)

* * *

## 功能对比

项目| 多 Token 支持| 批量操作| 白名单| 告警通知| 多人协作| 准确度| 特色  
---|---|---|---|---|---|---|---  
GSIL| ✓| ✕| ✕| 邮件| ✕| 中等| 自动克隆异常仓库  
Hawkeye| ✓| ✓| 关键字 / 文件名| 邮件 / 钉钉 / 企业微信| -| 较好| -  
码小六| ✓| ✓| 仓库 / 文件名| 邮件 / WebHook / Telegram / 钉钉 / 企业微信| ✓| 较好| 移动版 / 代理配置  
Github-Monitor| ✓| ✕| 用户 / 关键字| 邮件| -| 较好| 细粒度白名单及告警配置  
Github leaked patrol| -| -| -| -| -| -| -  
  
### 多 Token 支持

GitHub 有反爬虫机制且提供了丰富的 API，因此评测项目无一例外都是通过 API 进行监控且支持配置多个 API Token 突破请求速率限制，其中
Hawkeye 与码小六在界面上能直接查看 Token 的请求配额与状态，码小六支持自动根据 Token 请求配额进行调度及剔除失效 Token。

### 多人协作

多人协作可以方便安全团队轮班处理扫描结果，Hawkeye、码小六、GitHub-Monitor 均可对扫描记录设置状态，方便跟进处理。其中 Hawkeye
没有用户模块，码小六支持多用户，GitHub-Monitor 支持单用户，不支持多用户的项目，需要大家使用相同身份，无法查看个人的操作记录，稍微有些不便。

### 准确度

GitHub 基于 ElasticSearch
集群对外提供全文搜索服务，在建立倒排索引时，代码会被分词，这也导致了以上项目均会出现在扫描一些关键词时出现非相关结果，其中码小六和 GitHub-Monitor 在扫描时会对部分扫描结果做二次验证，扫描准确度略好，但差别不大。

### 特色功能

GSIL 支持自动将异常仓库克隆至本地，可以有效做到证据保全，由于会扫描到大量不相关项目，需定期清理磁盘。

码小六支持移动端，体验还不错！代理配置功能也挺实用，毕竟国内特殊的网络环境有时访问 GitHub 不太通畅。

GitHub-Monitor 提供了细粒度配置，可以配置每一个任务的白名单及告警通知，十分灵活，但是在企业级场景，需要扫描的关键词非常多，逐一配置略显麻烦。

* * *

## 综合点评

### GSIL

作者 FEEI 对代码安全做了深入的研究，从其文章 [《GitHub
敏感信息泄露监控》](https://esbp.feei.cn/vulnerabilities/gsil)便知一二，但是此项目功能简单，扫描结果通过邮件推送，
**适合个人学习使用，不推荐企业部署** 。

### Hawkeye

Hawkeye 是几个项目中最早开发的， **使用体验不错，但有一些问题迟迟没有修复** ，如 “泄露详情” - “快速排查” 无法使用，又如 GitHub
官方将于 2021 年 8 月 13 日起只接收 Token 方式验证身份（[Token authentication requirements for
Git operations](https://github.blog/2020-12-15-token-authentication-requirements-for-git-operations/)），Hawkeye 配置界面依旧是即将被禁用的 “用户名 + 密码” ，作者仅在
README.md 中做了提示，或许没有用心在维护了吧。

### 码小六

码小六起步最晚，但也是目前 **最活跃、完成度最高的项目，推荐使用**
。当然，码小六也有一些小问题，如告警通知没有详细信息，只提示当前时段有多少条记录。又如新增用户需要在命令行上执行，而不能通过页面注册。

### GitHub-Monitor

GitHub-Monitor **界面美观，使用体验有待提升** ，如不支持扫描结果批量操作、没有全局白名单及告警通知配置、扫描结果较多时显示不佳等。

### Github leaked patrol

似乎是无人维护，文档不全， **不推荐使用** ！

