# csaw

## 基本信息

| 字段 | 内容 |
| --- | --- |
| 来源 | CSAW Intro / CSAW CTF 2016 练习合集 |
| 方向 | Reverse / Pwn / Pyjail |
| 整理状态 | 多题混放，部分可复现 |

## 原始题目

历史目录混放 Baby's First、My First Pwnie、Target Practice 和 warmup_csaw_2016。

> 说明：仓库历史中没有保存官方平台题面文本。以上描述由本目录的原始附件复原；赛事或题意中标注“待核实”的部分不能视为官方原文。

## 附件

| 文件 | 用途 |
| --- | --- |
| `.gdb_history` | 附件 |
| `babysfirst.py` | 源码或辅助脚本 |
| `bot_send.py` | 源码或辅助脚本 |
| `flag.txt` | 题目输入/输出 |
| `my_first_pwnie.py` | 源码或辅助脚本 |
| `target_practice` | 附件 |
| `target_practice.py` | 源码或辅助脚本 |
| `test.py` | 解题/实验脚本 |
| `warmup_csaw_2016` | 附件 |
| `warmup_csaw_2016.py` | 源码或辅助脚本 |
| `whataxor.cpp` | 源码或辅助脚本 |

子目录中的文件同样属于原始材料；为避免破坏历史记录，本次整理没有移动、重命名或删除附件。

## Writeup

### 思路

Baby's First 直接阅读源码；My First Pwnie 利用 eval；Target Practice/warmup 通过栈溢出跳转目标函数。后续应逐题拆目录。

### 复现

```bash
cd "csaw"
python3 babysfirst.py
```

运行未知二进制、网络利用脚本或容器前请先阅读源码，并在隔离环境中操作。历史远程地址通常已经失效，默认应改成本地进程。

## 待办

- [ ] 核对官方题面、分值、作者与附件哈希
- [ ] 将实验脚本整理成确定性的 `solve.py`
- [ ] 记录依赖版本、完整推导和预期输出
- [ ] 在隔离环境完成本地复现
