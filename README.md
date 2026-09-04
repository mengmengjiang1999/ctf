# CTF 题目与 Writeup 归档

[![Public audit](https://github.com/mengmengjiang1999/ctf/actions/workflows/public-audit.yml/badge.svg)](https://github.com/mengmengjiang1999/ctf/actions/workflows/public-audit.yml)

这是一个 CTF 学习与复现仓库，包含 Crypto、Pwn、Reverse、Web、Misc 等方向的题目附件、实验脚本和部分 writeup。

> **剧透与安全提示：**仓库包含题目答案、flag、利用脚本和来源不一的可执行文件。请只在获得授权的题目环境中使用；浏览 writeup 前请注意剧透，不要在宿主机直接运行未知附件。

仓库最初是一次性上传的个人记录：文件命名和目录层级不统一，部分脚本未完成，也有编译产物、IDA 数据库及第三方工具。本轮整理遵循“保留题目附件、先补文档、逐题验证”的原则；只移除了可再生成的缓存、编辑器数据库和调试日志。

## 快速导航

| 方向/赛事 | 内容 | 状态 |
| --- | --- | --- |
| [`reverse/buuoj`](reverse/buuoj/) | BUUOJ Reverse 练习，含 usualCrypt、IgniteMe、Cr0ssfun、level3 等 | 多数已有 solve 草稿 |
| [`pppppwn`](pppppwn/) | BUUOJ/THUCTF Pwn 练习 | 多为硬编码远程脚本，需本地化 |
| [`crypto`](crypto/) | RSA、DLP 与基础编码练习 | 完成度不一 |
| [`secconctf`](secconctf/) | SECCON CTF 2023 Finals 附件 | 多数缺 solve |
| [`qwb2023`](qwb2023/) | 强网杯 2023 Crypto/Misc | 多数缺 writeup |
| [`ctfpractice/THUCTF2023`](ctfpractice/THUCTF2023/) | 自制/改编的 THUCTF 题目包 | 已有部分题面与 writeup |
| [`lab1`](lab1/) | 课程实验：编码、AES、格式化字符串、栈溢出 | 见 `report1.md`、`report2.md` |
| [`tctf2023`](tctf2023/) | Castling 等密码/逆向实验 | 草稿 |
| [`misc/pre`](misc/pre/) | 二维码图片处理题 | 已有过程记录 |

每个已识别的独立题目目录都配有 `README.md`，内容包括：从本地附件复原的题面、附件说明、现有解题思路、复现入口和缺口。官方题面未保存在历史仓库中的，统一标注“待核实”，不会伪装成官方原文。

## 推荐阅读顺序

1. 阅读 [题目清单](docs/inventory.md)，按来源、方向和完成度筛选题目。
2. 阅读 [整理约定](docs/organization.md)，了解状态定义和安全边界。
3. 查看 [已核验的外部来源](docs/sources.md)，区分官方资料与第三方 writeup。
4. 使用 [`docs/SHA256SUMS`](docs/SHA256SUMS) 核对历史附件是否被改动。
5. 从清单进入题目目录，查看该题 `README.md`。
6. 先阅读附件和脚本，再在隔离环境中复现；不要直接运行来源不明的二进制。
7. 使用 [题目模板](docs/challenge-template.md) 补充官方题面、附件哈希和完整 writeup。

## 当前主要缺口

- 多数目录缺少官方题面原文、作者、分值和稳定来源链接。
- 一些目录只保存了解题脚本，没有原始二进制；另一些只有附件，没有 solve。
- 多个 Pwn 脚本写死了已经失效的 BUUOJ 地址，应改为“本地默认、远程可选”。
- `pk/pkcrack-1.2.2`、`tctf2023/binaryai` 下包含第三方源码，后续需要补许可证与来源。
- Git 历史中仍存在早期缓存和大型逆向数据库；当前版本已清理可再生成文件，但彻底缩减历史体积仍需单独执行历史重写。

## 贡献要求

新增或完善题目时，请至少提交：

- 官方题面或可靠来源链接（注明访问日期）；
- 原始附件及 SHA-256；
- 能从附件独立得到结果的 `solve.py`；
- 解释关键漏洞/算法、完整复现命令和依赖版本的 `README.md`。

仅含 flag 或只粘贴脚本的记录不算完整 writeup。

详细流程见 [贡献指南](CONTRIBUTING.md)。提交前可运行：

```bash
python3 scripts/public_audit.py
python3 scripts/generate_challenge_docs.py
git diff --check
```

## 许可与第三方内容

仓库作者原创代码采用 MIT License，原创文档与 writeup 采用 CC BY 4.0；比赛附件、二进制和第三方源码不因此获得重新许可。使用或分发前请阅读 [LICENSE](LICENSE) 与 [第三方内容说明](THIRD_PARTY_NOTICES.md)。安全问题或误提交的敏感信息请按 [安全策略](SECURITY.md) 处理。
