#!/usr/bin/env python3
"""Generate conservative README files for legacy challenge directories.

The repository was imported as a single historical snapshot.  This script does
not rename or delete any artifact and never overwrites an existing README.
Metadata below records only what can be inferred from the checked-in material.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_DOCUMENTS = {
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "THIRD_PARTY_NOTICES.md",
}


# path: (event/platform, category, statement, approach, status, run hint)
CHALLENGES = {
    "blackhat": (
        "Black Hat training（具体场次待核实）", "合集 / Reverse",
        "本目录除三个已拆分题目外，还保存 `WhatAmI.zip`；压缩包内是 `WhatAmI.dll`，应按 .NET 逆向题处理。",
        "使用 dnSpy/ILSpy 等静态检查 DLL；其余题目进入各子目录查看。", "合集索引，WhatAmI 待解", "unzip -l WhatAmI.zip",
    ),
    "blackhat/crypto": (
        "Black Hat training（具体场次待核实）", "Crypto",
        "逆向三层加密：ChaCha20 加密 flag、固定字符串异或混淆密钥、再以小模数 RSA 逐字符加密密钥。",
        "题目直接给出 RSA 私钥，先解开 `Encrypted Message`，Base64 解码并撤销循环异或得到 ChaCha20 key，再结合 nonce 解密 flag。", "题面与算法可复原", "python3 crypto.py",
    ),
    "ccb/crypto": (
        "CCB（具体赛事待核实）", "Crypto / RSA",
        "已知 n、c 以及 `(p+q) >> 233`，恢复 p、q 并解密。",
        "泄露的是 p+q 的高位。应使用 Coppersmith/格方法恢复低 233 位；现有 `ans.py`、`ans2.py` 直接枚举 2^100 量级，实际不可行。", "错误/未完成解法", "python3 task.py",
    ),
    "crypto/buuoj/base64flag": (
        "BUUOJ Crypto（具体题名待核实）", "Crypto / Encoding",
        "根据目录内的编码文本与实验脚本还原变体 Base64 内容。",
        "对照 `base.py`、`basic.py`、`test.py` 的字符表与输入逐层验证。异常文件名受 Unicode 规范化影响，需要在 Linux 上核对原名。", "解题草稿", "python3 base.py",
    ),
    "crypto/buuoj": (
        "BUUOJ Crypto 入门练习合集", "Crypto / Encoding",
        "目录顶层混放签到、ASCII、凯撒、键盘密码、摩斯、MD5、Quoted-Printable 等基础编码题。",
        "按文件名选择对应标准解码方式；RSA 与 base64flag 等较大题目已位于子目录。后续应把每个顶层脚本和输入拆成独立题目目录。", "多题混放，待二次拆分", "find . -maxdepth 1 -type f -print",
    ),
    "crypto/buuoj/rsa": (
        "BUUOJ Crypto 练习合集", "Crypto / RSA",
        "该历史目录混放 BabyRSA、rsaroll、共模/低指数等多道 RSA 练习的附件和脚本。",
        "先按同名前缀配对题目与脚本；`BabyRsa.py`、`bbbbrsa.py`、`drsa.py`、`rsa*.py`、`rsaroll.py` 分别是独立解题记录。后续应逐题拆目录。", "多题混放，待二次拆分", "file BabyRsa bbbbrsa flag.enc pub.key",
    ),
    "crypto/buuoj/yxxx": (
        "BUUOJ Crypto（题名待核实）", "Crypto",
        "根据 `c.txt` 与 `key.txt` 恢复密文；`yxxx.py` 是现有实验文件。",
        "先识别 `key.txt` 与 `c.txt` 的编码/数据格式，再核对 `yxxx.py` 的逆变换。", "材料待核实", "file c.txt key.txt yxxx.py",
    ),
    "crypto/csaw": (
        "CSAW（具体年份待核实）", "Crypto / Probability",
        "在每轮 1..70 中选 6 个数的百万轮彩票中，用最多 40 张票保证每轮获利。",
        "漏洞是 ticket 内数字没有去重，但匹配时会转为 set；需构造覆盖组合并验证收益表。仓库只有服务端。", "待补 solve/writeup", "python3 server.py",
    ),
    "csaw": (
        "CSAW Intro / CSAW CTF 2016 练习合集", "Reverse / Pwn / Pyjail",
        "历史目录混放 Baby's First、My First Pwnie、Target Practice 和 warmup_csaw_2016。",
        "Baby's First 直接阅读源码；My First Pwnie 利用 eval；Target Practice/warmup 通过栈溢出跳转目标函数。后续应逐题拆目录。", "多题混放，部分可复现", "python3 babysfirst.py",
    ),
    "ctfpractice/THUCTF2023/maze": (
        "THUCTF 2023 自制题", "Misc / Reverse",
        "从图片隐写中提取逆序 ZIP，得到二进制后分别恢复静态 flag 与正确迷宫输入。",
        "`mark.md` 记录了出题链：编译 `puzzle.cpp`、压缩二进制、反转 ZIP 后写入图片；`pack/README.md` 与 `pack/write-up.md` 保存发布版题面和解答。", "已有题面与 writeup", "python3 reversezip.py",
    ),
    "ctfpractice/THUCTF2023/base64andquipquip": (
        "THUCTF 2023 自制题", "Crypto / Encoding",
        "先解自定义 Base64，再对替换密码文本进行频率分析，得到两段 flag。",
        "发布版题面和 writeup 已保存在 `pack/`；根目录 README 记录出题材料。", "已有题面与 writeup", "find pack -maxdepth 2 -type f -print",
    ),
    "ctfpractice/THUCTF2023/yahaha": (
        "THUCTF 2023 自制题", "Misc / Steganography",
        "比较经过修改的图片并恢复隐藏内容。",
        "根目录 README、生成脚本和校验脚本组成现有题目记录；`pkuversion/` 是另一 flag 格式版本。", "已有题面/出题记录", "python3 verify.py",
    ),
    "ctfpractice/THUCTF2023/base64(failed)": (
        "THUCTF 2023 失败原型", "Crypto / Encoding",
        "自定义 Base64 题目的早期失败版本，不作为正式赛题。",
        "保留用于追踪出题迭代；正式版本见 `../base64andquipquip/`。", "历史原型", "python3 baseEncode.py",
    ),
    "ctfpractice/THUCTF2023/quip(failed)": (
        "THUCTF 2023 失败原型", "Crypto / Substitution",
        "替换密码题目的早期失败版本，不作为正式赛题。",
        "保留 `generator.py`、`timu.txt` 和测试 flag 用于追踪出题迭代。", "历史原型", "python3 generator.py",
    ),
    "dang_wan": (
        "来源待核实", "Pwn / Reverse",
        "分析 `dang_van` ELF 并恢复或利用目标逻辑。",
        "仓库只有未剥离二进制，没有题面、脚本或 writeup。", "材料不完整", "file dang_van",
    ),
    "debug_me": (
        "来源待核实", "Reverse",
        "从 `debug_me` 二进制的交错字符串索引逻辑恢复 12 字节输入。",
        "按 i % 3 选择字符串，按 2*(i/3) 选择字符并减 1；`test.cpp`/`test.py` 是等价重建。", "solve 可用", "python3 test.py",
    ),
    "flag_finder": (
        "来源待核实", "Reverse",
        "分析无符号表的 `flag_finder` ELF 并恢复 flag。",
        "仓库只有二进制和 pwndbg 记录目录，没有脚本或结论。", "材料不完整", "file flag_finder",
    ),
    "float": (
        "来源待核实", "Pwn / Reverse",
        "分析 `float` ELF 中与浮点数相关的校验或内存破坏。",
        "仓库只有二进制，没有题面和解题脚本。", "材料不完整", "file float",
    ),
    "lab1/base64": (
        "课程 Lab 1", "Reverse / Encoding",
        "逆向自定义 Base64 字符表并恢复 flag。",
        "用 `str.translate` 将修改后的字符表映射回标准 Base64 表后解码；完整说明见 `../report1.md`。", "已有报告", "python3 table.py",
    ),
    "lab1/aeslab": (
        "课程 Lab 1", "Reverse / Crypto",
        "先撤销自定义 Base64，再用程序内 16 字节密钥逆向 AES 处理。",
        "`test.py` 验证换表，`test2.py` 保存密文和密钥分析，完整说明见 `../report1.md`。", "已有报告，脚本待收尾", "python3 test.py",
    ),
    "lab1/fmt": (
        "课程 Lab 1", "Pwn / Format String",
        "利用格式化字符串读取 BSS 中的随机口令并回传。",
        "将目标地址放入输入，再用 `%s` 泄露 4 字节小端口令；完整说明见 `../report2.md`。", "已有报告", "python3 test.py",
    ),
    "lab1/overflow": (
        "课程 Lab 1", "Pwn / Stack Overflow",
        "利用栈溢出将相邻浮点变量改为 11.28125。",
        "填充到变量偏移并写入 `struct.pack('<f', 11.28125)`；完整说明见 `../report2.md`。", "已有报告", "python3 test.py",
    ),
    "lab1/overflow2": (
        "课程 Lab 1", "Pwn / Stack Overflow",
        "考虑字符串替换导致的长度增长，覆盖返回地址跳转后门。",
        "利用程序把 `I` 替换为更长字符串的行为调整输入布局，再写入 0x8048f0d；完整说明见 `../report2.md`。", "已有报告", "python3 test.py",
    ),
    "praymoon": (
        "来源待核实", "Kernel Pwn",
        "分析 `praymoon.tar.gz` 中的 Linux 内核、rootfs 与启动脚本并构造利用。",
        "原始包包含 `bzImage`、`rootfs.cpio`、`run.sh`；尚未保存漏洞模块源码或 writeup，需先安全解包核对 rootfs。", "待补 writeup", "tar -tzf praymoon.tar.gz",
    ),
    "reverse/rebug": (
        "CSAW Intro（来源待核实）", "Reverse",
        "提供任意 12 字节输入，程序计算固定字符串 `12` 的 MD5 并按 flag 格式输出。",
        "长度检查通过后输出只依赖固定 MD5；`test.cpp` 是反编译逻辑的重建。", "题意可复原", "./rebug",
    ),
    "reverse/trycatch": (
        "来源待核实", "Reverse",
        "分析带 C++ 异常控制流的 `trycatch` 二进制。",
        "目录只保存二进制及分析数据库，尚无文字记录。", "待补 writeup", "file trycatch",
    ),
    "simulator": (
        "来源待核实", "Reverse",
        "分析 `simulator` 如何解释 `input.bin`，构造或恢复目标输入。",
        "仓库只有二进制与输入数据，没有解题脚本。", "材料不完整", "file simulator input.bin",
    ),
    "sqlblindin": (
        "来源待核实", "Web / SQL Injection",
        "对目标服务进行布尔/时间盲注并恢复数据。",
        "`exp.py` 当前为空，且没有保存目标源码或请求格式。", "材料不完整", "wc -c exp.py",
    ),
    "stackoverflow": (
        "栈溢出练习合集", "Pwn",
        "目录混放 ret2win、ret2libc、静态 ROP 等多道基础栈溢出练习。",
        "`bug.c`/`test.py` 是 64 位 ret2win；`level2.py` 和 `pwn0.py` 构造 system('/bin/sh')；`pwn2.py` 尚未完成。后续应逐题拆分。", "多题混放，部分可复现", "cc bug.c -o bug",
    ),
    "web": (
        "来源待核实", "Web / SSTI",
        "通过模板注入枚举 Python 对象子类，定位 `catch_warnings` 等可利用类。",
        "`ezssti.py` 枚举 `object.__subclasses__()` 的索引；目标地址是历史环境，默认不要连接。", "解题草稿", "python3 ezssti.py",
    ),
    "blackhat/Simple Encryption": (
        "Black Hat training（具体场次待核实）", "Crypto",
        "分析 `chal.py` 给出的加密流程，并根据 `output.txt` 恢复明文。",
        "从加密脚本提取算法与参数，逆向对应变换。", "待补全", "python3 chal.py",
    ),
    "blackhat/player": (
        "Black Hat training（具体场次待核实）", "Pwn",
        "审计容器中的 `main.c`，利用程序缺陷取得目标信息。",
        "先阅读源码和容器配置，再在隔离环境中复现漏洞。", "待补全", "docker compose up --build",
    ),
    "blackhat/rsa": (
        "Black Hat training（具体场次待核实）", "Crypto",
        "连续完成三个 RSA 小挑战：由 n 与 φ(n) 分解、由 φ(n) 的倍数分解、利用解密 oracle。",
        "分别使用二次方程、随机取底的因数恢复法，以及教科书 RSA 的可乘性。", "题面可复原，解答待整理", "python3 chal.py",
    ),
    "ccb/fragile": (
        "CCB（具体赛事待核实）", "Crypto",
        "根据 `task.py`、`output.txt` 中的 RSA 变体参数恢复 flag。",
        "现有 `writeup.md` 通过分解构造出的乘积，并结合 a、b 的位数与大小约束筛选因子。", "已有完整 writeup", "python3 ans.py",
    ),
    "crypto/ezDLP": (
        "来源待核实", "Crypto",
        "已知 p、g 与 a = g^x mod p^q，其中 q 是 9 位素数；恢复嵌入 x 的 flag。",
        "利用特殊模数 p^q 与指数结构分析离散对数；仓库目前只有出题脚本和输出。", "待补 solve/writeup", "python3 task.py",
    ),
    "crypto/ezrsa": (
        "来源待核实", "Crypto",
        "根据 `task.py` 生成的 RSA 参数与 `output.txt` 恢复明文。",
        "对照 `test.py` 中的试验代码检查模数、指数或素数生成方式的弱点。", "解题草稿", "python3 test.py",
    ),
    "crypto/rsa-dp": (
        "来源待核实", "Crypto",
        "利用泄露的 CRT 指数信息（dp）恢复 RSA 私钥并解密。",
        "枚举满足 e·dp-1 = k(p-1) 的小整数 k，恢复 p 后计算 d。", "解题草稿", "python3 test.py",
    ),
    "crypto/rsa-factor": (
        "来源待核实", "Crypto",
        "利用题目额外泄露的信息分解 RSA 模数并恢复 flag。",
        "以 `test.py` / `ttt.py` 为现有试验入口；先确认使用的是哪份 output。", "解题草稿", "python3 test.py",
    ),
    "crypto/rsa-weiner": (
        "来源待核实", "Crypto",
        "针对私钥指数过小的 RSA 参数恢复明文。",
        "对 e/n 做连分数展开，枚举收敛分数并验证候选 φ(n)（Wiener attack）。", "待补 solve/writeup", "python3 task.py",
    ),
    "crypto/rsa4": (
        "来源待核实", "Crypto",
        "分析 `rsa.tar.gz` 中的原始题目包并完成 RSA 题。",
        "原始压缩包已保留；需要先核对解包后的 `dist/` 内容。", "待补 writeup", "tar -tzf rsa.tar.gz",
    ),
    "final/rsa": (
        "课程/决赛题（来源待核实）", "Crypto",
        "分析 `233.tar` 中的 RSA 附件并恢复明文。",
        "原始压缩包及解包后的 attachment 已保留，尚无可靠解题记录。", "待补 writeup", "tar -tf 233.tar",
    ),
    "misc/pre": (
        "校内赛前置题（来源待核实）", "Misc / QR",
        "从多张经过混合或变换的二维码图片中恢复最终信息。",
        "现有脚本覆盖图片转换、二维码生成/混合与结果校验；`timu.md` 和 `readme.md` 是原有记录。", "已有过程记录", "python3 check_final.py",
    ),
    "pppppwn/baby_stack": (
        "THUCTF 2021", "Pwn",
        "分析 `stack` 并构造利用。历史脚本连接已下线的远程服务。",
        "现有脚本直接发送 shellcode；完整前提与控制流仍需从二进制核验。", "已有简短 writeup", "python3 stack.py",
    ),
    "pppppwn/ciscn": (
        "CISCN 2019 / BUUOJ", "Pwn",
        "利用 `ciscn_2019_n_1` 的栈溢出改变关键浮点比较值。",
        "填充到目标变量并写入 11.28125 对应的浮点字节；现有脚本写入 0x41348000。", "可复现草稿", "python3 ciscn_2019_n_1.py",
    ),
    "pppppwn/csaw": (
        "CSAW CTF 2016 / BUUOJ", "Pwn",
        "利用 warmup 程序的栈溢出跳转到输出 flag 的函数。",
        "覆盖 0x48 字节缓冲区与保存的 RBP，将返回地址改为 0x40060d。", "可复现草稿", "python3 warmup_csaw_2016.py",
    ),
    "pppppwn/jarvisoj": (
        "Jarvis OJ level0 / BUUOJ", "Pwn",
        "利用 64 位程序的栈溢出跳转到 callsystem。",
        "使用 136 字节填充后覆盖返回地址为 0x400596。", "可复现草稿", "python3 level0.py",
    ),
    "pppppwn/rip1": (
        "BUUOJ（具体题名待核实）", "Pwn",
        "分析 `pwn1` 并完成远程利用。",
        "现有脚本只有连接逻辑，没有 payload。", "未完成", "python3 rip1.py",
    ),
    "pppppwn/sctf": (
        "SCTF 2016 / BUUOJ", "Pwn",
        "利用 `pwn1_sctf_2016` 的输入替换与栈溢出控制返回地址。",
        "利用 replace 导致长度增长，按脚本布局覆盖返回地址到 0x8048f0d。", "可复现草稿", "python3 pwn1_sctf_2016.py",
    ),
    "qwb2023/babyrsa": (
        "强网杯 2023", "Crypto",
        "根据 `task.py` 中泄露的 RSA 相关量恢复 flag。",
        "仓库只有题目脚本，尚未保存输出与解答。", "材料不完整", "python3 task.py",
    ),
    "qwb2023/discrate_log": (
        "强网杯 2023", "Crypto",
        "根据 `task.py` 和 `out.txt` 求解离散对数变体。",
        "从群阶分解与泄露关系入手；仓库尚无 solve。", "待补 solve/writeup", "python3 task.py",
    ),
    "qwb2023/shortpy": (
        "强网杯 2023", "Misc / Pyjail",
        "审计受限 Python 服务，在字符/长度限制下读取目标信息。",
        "服务源码位于 `server/src`，Docker 配置可用于隔离复现。", "待补 writeup", "docker compose up --build",
    ),
    "reverse/buuoj/ACTF新生赛2020usualCrypt": (
        "ACTF 新生赛 2020 / BUUOJ", "Reverse",
        "逆向魔改 Base64 校验程序，恢复正确输入。",
        "先交换密文大小写，再还原被交换区段的 Base64 表，最后标准 Base64 解码。", "solve 可用", "python3 ans.py",
    ),
    "reverse/buuoj/FlareOn4IgniteMe": (
        "FLARE-On 4 / BUUOJ", "Reverse",
        "逆向逐字节异或校验逻辑，恢复输入。",
        "先用初始值修正末字节，再从后向前执行相邻字节异或的逆运算。", "solve 可用", "python3 ans.py",
    ),
    "reverse/buuoj/GWCTF 2019xxor": (
        "GWCTF 2019 / BUUOJ", "Reverse",
        "逆向 64 轮类 TEA 变换与输入约束。",
        "先解线性约束得到 6 个 32 位字，再逆向轮函数。现有脚本停在轮函数，尚未完成。", "未完成", "python3 ans.py",
    ),
    "reverse/buuoj/HDCTF2019Maze": (
        "HDCTF 2019 / BUUOJ", "Reverse",
        "从程序数据段还原迷宫并给出从起点到终点的移动序列。",
        "按固定行宽打印迷宫，识别起点/终点后得到 `ssaaasaassdddw`。", "solve 可用", "python3 ans.py",
    ),
    "reverse/buuoj/MRCTF2020Xor": (
        "MRCTF 2020 / BUUOJ", "Reverse",
        "逆向按索引异或的字符串校验。",
        "逐字节计算 ciphertext[i] XOR i 即可恢复 flag。", "solve 可用", "python3 ans.py",
    ),
    "reverse/buuoj/MRCTF2020hello_world_go 1": (
        "MRCTF 2020 / BUUOJ", "Reverse",
        "分析 Go 二进制 `hello_world_go` 并恢复 flag。",
        "仓库仅保存二进制和 IDA 数据库，没有解题记录。", "待补 writeup", "file hello_world_go",
    ),
    "reverse/buuoj/SUCTF2019SignIn": (
        "SUCTF 2019 / BUUOJ", "Reverse / Crypto",
        "分解程序内的 RSA 参数并逆向十六进制字符编码。",
        "使用已知 p、q 计算 d，RSA 解密后将成对十六进制字符还原为字节。", "solve 可用", "python3 ans.py",
    ),
    "reverse/buuoj/WUSTCTF2020Cr0ssfun": (
        "WUSTCTF 2020 / BUUOJ", "Reverse",
        "从层层函数调用中的字符约束恢复输入。",
        "按每个位置的比较常量重排 33 个字符；也可按官方 writeup 使用 angr 搜索成功输出。", "solve 可用", "python3 ans.py",
    ),
    "reverse/buuoj/WUSTCTF2020level": (
        "WUSTCTF 2020 / BUUOJ", "Reverse",
        "分析附件中的简单校验逻辑并取得 flag。",
        "原有 `record.md` 保存了分析记录；目录同时保留新旧附件。", "已有记录", "file attachment",
    ),
    "reverse/buuoj/WUSTCTF2020level3": (
        "WUSTCTF 2020 / BUUOJ", "Reverse",
        "逆向被修改字典的 Base64 编码。",
        "恢复 Base64 表前 20 个字符的对称交换，再解码内置密文。", "solve 可用", "python3 base.py",
    ),
    "reverse/buuoj/easyre": (
        "ACTF / BUUOJ（具体场次待核实）", "Reverse",
        "脱去 UPX 后分析字符表查找逻辑，恢复 ACTF 格式输入。",
        "固定前后缀后，对中间 12 字节在倒序字符表中反查索引。", "已有分析记录", "python3 easyre.py",
    ),
    "reverse/buuoj/level1": (
        "BUUOJ（具体赛事待核实）", "Reverse",
        "根据 `output.txt` 中逐行整数恢复字符。",
        "奇数位置右移对应位数，偶数位置除以位置序号。", "solve 可用", "python3 att.py",
    ),
    "reverse/buuoj/login": (
        "BUUOJ（具体赛事待核实）", "Reverse",
        "逆向 JavaScript 风格的 ROT13 登录校验。",
        "现有脚本记录了字符边界分析，但最终恢复逻辑仍需校正。", "未完成", "python3 login.py",
    ),
    "reverse/buuoj/lucky_guy": (
        "GXYCTF / BUUOJ", "Reverse",
        "逆向分支选择与逐字节减法，恢复 `GXY{...}` 格式输入。",
        "将内置 8 字节常量逆序，按索引奇偶分别减 2 或减 1。", "solve 可用", "python3 test.py",
    ),
    "reverse/buuoj/mrctf2020transform": (
        "MRCTF 2020 / BUUOJ", "Reverse",
        "逆向索引置换与异或变换。",
        "对每个 i 执行 flag[index[i]] = data[i] XOR index[i]。", "solve 可用", "python3 ans.py",
    ),
    "reverse/buuoj/pyc": (
        "BUUOJ（具体赛事待核实）", "Reverse",
        "反编译 Python 2 字节码并逆向相邻异或和索引偏移。",
        "先从后向前撤销 code[i] ^= code[i+1]，再减去每个位置的索引。", "solve 可用", "python3 anss.py",
    ),
    "reverse/buuoj/re": (
        "BUUOJ（题名待核实）", "Reverse",
        "根据程序中的算术约束恢复 32 字节输入，并爆破缺失字符。",
        "用常量除法逐位恢复；第 7 字节通过调用本地二进制枚举可打印字符。", "solve 可用但会覆盖临时输出", "python3 ans.py",
    ),
    "reverse/buuoj/rome": (
        "BUUOJ（题名 Rome）", "Reverse",
        "逆向大小写分别处理的凯撒移位。",
        "对大写与小写字符使用不同偏移做模 26 逆变换，保留非字母字符。", "solve 可用", "python3 rome.py",
    ),
    "sandbox/crabox": (
        "SECCON 系列（具体场次待核实）", "Misc / Sandbox",
        "审计 Flask 服务及其沙箱限制，构造能够读取目标信息的输入。",
        "先用 Docker 隔离启动，重点检查 `app.py` 的过滤和执行边界。", "待补 writeup", "docker compose up --build",
    ),
    "secconctf/DLP": (
        "SECCON CTF 2023 Finals", "Crypto",
        "DLP 4.0：分析 `problem.sage` 中的离散对数构造并恢复 flag。",
        "原始题目源码和容器配置已保存；仓库尚无 solve。", "待补 solve/writeup", "sage problem.sage",
    ),
    "secconctf/digitcake": (
        "SECCON CTF 2023 Finals", "Pwn / Reverse",
        "分析 `digicake.c` 的数字处理逻辑并构造满足条件的输入。",
        "源码是原始附件；尚无解题记录。", "待补 writeup", "cc digicake.c -o digicake",
    ),
    "secconctf/muck-a-mac": (
        "SECCON CTF 2023 Domestic Finals", "Crypto",
        "在 100 轮交互中利用 MAC 接口恢复随机明文。",
        "审计可选操作对 ciphertext、AAD、长度和明文异或的影响，组合泄露恢复每轮 plaintext。", "待补 solve/writeup", "python3 problem.py",
    ),
    "secconctf/parllier": (
        "SECCON CTF 2023 Domestic Finals", "Crypto",
        "Paillier 4.0：分析原始压缩包中的 Paillier 变体。",
        "原始包和 `dist/` 已保留，尚无可靠解题记录。", "待补 writeup", "tar -tzf Paillier_4.0.tar.gz",
    ),
    "secconctf/rsa-kex": (
        "SECCON CTF 2023 Domestic Finals", "Crypto",
        "KEX 4.0：分析原始包中的密钥交换与后续加密。",
        "题目包和 `dist/` 已保留，尚无 solve。", "待补 writeup", "tar -tzf dist.tar.gz",
    ),
    "secconctf/v_v_m_m_v_m_m": (
        "SECCON CTF 2023 Domestic Finals", "Crypto",
        "分析 `problem.sage` 中的格/矩阵构造并恢复 flag。",
        "`doc.md` 目前只记录环境依赖，不是解题 writeup。", "待补 solve/writeup", "sage problem.sage",
    ),
    "tctf2023/castling": (
        "TCTF 2023（归属待核实）", "Crypto / Hash",
        "分析基于 DES 结构的自定义哈希并构造碰撞。",
        "现有 `generate.py`、`collision.py` 和 HTTP 提交脚本是实验记录，需统一到 Python 3 并验证。", "解题草稿", "python3 generate.py",
    ),
    "tctf2023/binaryai": (
        "TCTF 2023（归属待核实）", "Reverse / AI",
        "历史目录保存 BinaryAI 相关试验与多个上游项目源码。",
        "`try/` 是本地实验；Reptile、libsodium、st-device-sdk-c 看起来是第三方依赖，不应当成独立赛题。需要补原始附件与依赖版本。", "材料待核实", "find try -maxdepth 1 -type f -print",
    ),
    "tctf2023/castling2": (
        "TCTF 2023（归属待核实）", "Crypto",
        "分析固定密钥、无链式模式的类 MD5 分组加密并恢复 ciphertext。",
        "每个 16 字节块独立，可逆向 64 轮；`decrypt.py` 仍为空。", "未完成", "python3 task.py",
    ),
    "tctf2023/rwc": (
        "TCTF 2023（归属待核实）", "Reverse / Crypto",
        "分析 `task` 二进制和 `ciphertext`，恢复原始数据。",
        "仓库没有分析脚本或 writeup。", "待补 writeup", "file task ciphertext",
    ),
    "thuctf2023/babystack": (
        "THUCTF 2023", "Pwn",
        "利用 `main` 的栈漏洞，结合随附 libc 与动态链接器构造利用。",
        "`babystack.py` 是现有利用入口；应优先改为本地模式并记录偏移与 ROP 链。", "解题草稿", "python3 babystack.py",
    ),
    "强网杯": (
        "强网杯（年份待核实）", "Crypto / RSA",
        "p、q 分别位于已知 a 两侧附近，并由一个 6 位素数 r 控制；分解 n 后解密 c。",
        "枚举 6 位素数 r，按题目方式生成 p、q，找到乘积等于 n 的组合后计算私钥。`task_solve.py` 尚未完成。", "未完成", "python3 task_solve.py",
    ),
}


def role(name: str) -> str:
    lower = name.lower()
    if lower.startswith("readme"):
        return "已有说明"
    if "writeup" in lower or lower in {"record.md", "recode.md", "mark.md", "doc.md"}:
        return "分析记录"
    if lower.startswith(("ans", "solve", "exp", "attack", "attact")) or lower in {
        "test.py", "base.py", "table.py", "rome.py", "stack.py", "babystack.py",
    }:
        return "解题/实验脚本"
    if lower.startswith(("task", "problem", "chal", "server", "main")):
        return "题目源码/程序"
    if lower.endswith((".tar", ".tar.gz", ".zip")):
        return "原始题目包"
    if lower.endswith((".py", ".sage", ".c", ".cpp", ".rs")):
        return "源码或辅助脚本"
    if lower.endswith((".txt", ".enc", ".hash", ".key", ".bin")) or lower in {"ciphertext", "output"}:
        return "题目输入/输出"
    return "附件"


def direct_files(directory: Path) -> list[Path]:
    return sorted(
        (p for p in directory.iterdir() if p.is_file() and p.name not in {".DS_Store", "README.md"}),
        key=lambda p: p.name.casefold(),
    )


def render(path: str, data: tuple[str, str, str, str, str, str]) -> str:
    event, category, statement, approach, status, run_hint = data
    directory = ROOT / path
    files = direct_files(directory)
    file_rows = "\n".join(f"| `{p.name}` | {role(p.name)} |" for p in files)
    if not file_rows:
        file_rows = "| （无顶层文件） | 请检查子目录 |"
    title = directory.name
    return f"""# {title}

## 基本信息

| 字段 | 内容 |
| --- | --- |
| 来源 | {event} |
| 方向 | {category} |
| 整理状态 | {status} |

## 原始题目

{statement}

> 说明：仓库历史中没有保存官方平台题面文本。以上描述由本目录的原始附件复原；赛事或题意中标注“待核实”的部分不能视为官方原文。

## 附件

| 文件 | 用途 |
| --- | --- |
{file_rows}

子目录中的文件同样属于原始材料；为避免破坏历史记录，本次整理没有移动、重命名或删除附件。

## Writeup

### 思路

{approach}

### 复现

```bash
cd "{path}"
{run_hint}
```

运行未知二进制、网络利用脚本或容器前请先阅读源码，并在隔离环境中操作。历史远程地址通常已经失效，默认应改成本地进程。

## 待办

- [ ] 核对官方题面、分值、作者与附件哈希
- [ ] 将实验脚本整理成确定性的 `solve.py`
- [ ] 记录依赖版本、完整推导和预期输出
- [ ] 在隔离环境完成本地复现
"""


def main() -> None:
    created = 0
    skipped = 0
    missing = []
    for path, data in CHALLENGES.items():
        directory = ROOT / path
        if not directory.is_dir():
            missing.append(path)
            continue
        readme = directory / "README.md"
        if readme.exists():
            skipped += 1
            continue
        readme.write_text(render(path, data), encoding="utf-8")
        created += 1
    rows = []
    for path, data in sorted(CHALLENGES.items(), key=lambda item: item[0].casefold()):
        event, category, _statement, _approach, status, _run_hint = data
        directory = ROOT / path
        readme_name = next(
            (p.name for p in directory.iterdir() if p.is_file() and p.name.casefold() == "readme.md"),
            "README.md",
        )
        encoded_path = path.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
        link = "../" + encoded_path + "/" + readme_name
        rows.append(f"| [`{path}`]({link}) | {event} | {category} | {status} |")
    inventory = """# 题目清单

本表由 `scripts/generate_challenge_docs.py` 中的保守元数据生成。状态只反映仓库现有材料，不表示已经在当前环境执行未知二进制或连接历史远程服务。

| 路径 | 来源 | 方向 | 当前状态 |
| --- | --- | --- | --- |
""" + "\n".join(rows) + "\n"
    (ROOT / "docs" / "inventory.md").write_text(inventory, encoding="utf-8")
    checksum_rows = []
    for artifact in sorted(ROOT.rglob("*"), key=lambda p: str(p.relative_to(ROOT)).casefold()):
        if not artifact.is_file():
            continue
        relative = artifact.relative_to(ROOT)
        if relative.parts[0] in {".git", ".github", ".vscode", "docs", "scripts"}:
            continue
        if (
            str(relative) in ROOT_DOCUMENTS
            or artifact.name.casefold() == "readme.md"
            or artifact.name == ".gitignore"
        ):
            continue
        digest = hashlib.sha256()
        with artifact.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        checksum_rows.append(f"{digest.hexdigest()}  {relative}")
    (ROOT / "docs" / "SHA256SUMS").write_text(
        "\n".join(checksum_rows) + "\n", encoding="utf-8"
    )
    print(f"created={created} skipped_existing={skipped} missing={len(missing)}")
    for path in missing:
        print(f"missing: {path}")


if __name__ == "__main__":
    main()
