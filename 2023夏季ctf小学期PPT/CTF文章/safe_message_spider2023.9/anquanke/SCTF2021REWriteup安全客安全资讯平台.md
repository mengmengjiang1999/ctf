# SCTF 2021 RE Writeup

阅读量 **181358**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-06 16:30:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0189f2ae4715b66457.jpg)

## 前言

年底了，2021年最后一场比赛，我就表演个AK RE给大伙助助兴吧。

比赛官网：<https://sctf2021.xctf.org.cn>  
比赛时间：2021-12-25 09:00:00 到 2021-12-27 09:00:00

## Reverse

###  SycGame

main中逻辑很简单，就是循环5次游戏，成功后拿到flag，关键在于sub_24E4的游戏逻辑。

    
    
    int __fastcall sub_24E4()
    {
      int v0; // eax
      int v1; // ebx
      int v2; // er12
      char v4; // [rsp+Bh] [rbp-15h]
      int i; // [rsp+Ch] [rbp-14h]
    
      srand(0);
      v0 = time(0LL);
      srand(v0 + srand_seed);
      srand_seed += rand();
      reset_globals();
      init_primes();
      size = 20;
      problem_size = 4;
      set_map();
      print_gift();
      null();
      printf("Tell me sol:");
      for ( i = 1; ; ++i )
      {
        if ( i > 10000 )
          fail();
        v4 = getchar();
        if ( v4 != '\n' )
          break;
    LABEL_26:
        ;
      }
      if ( v4 != 'w' && v4 != 's' && v4 != 'a' && v4 != 'd' && v4 != '0' )// 
                                                    // directions['w'] = 0;
                                                    // directions['s'] = 1;
                                                    // directions['a'] = 2;
                                                    // directions['d'] = 3;
        fail_0();
      if ( v4 == '0' )
        fail_1();
      if ( map[y_offset[directions[v4]]][3005 * y + x_offset[directions[v4]] + x] == -1 )// map[y + y_offset][x + x_offset]
      {
        if ( map[y_offset[directions[v4]]][3005 * y_offset[directions[v4]]
                                         + 3005 * y
                                         + x_offset[directions[v4]]
                                         + x
                                         + x_offset[directions[v4]]] == -3 )// map[y + y_offset * 2][x + x_offset * 2]
        {
          ++problem_solved;
          map[y_offset[directions[v4]]][3005 * y_offset[directions[v4]]// map[y + y_offset * 2][x + x_offset * 2]
                                      + 3005 * y
                                      + x_offset[directions[v4]]
                                      + x
                                      + x_offset[directions[v4]]] = -1;
          map[y_offset[directions[v4]]][3005 * y + x_offset[directions[v4]] + x] = -2;// map[y + y_offset][x + x_offset]
          map[y][x] = map_backup[y][x];
          y += y_offset[directions[v4]];
          x += x_offset[directions[v4]];
        }
        else
        {
          if ( !is_composite[map[y_offset[directions[v4]]][3005 * y_offset[directions[v4]]
                                                         + 3005 * y
                                                         + x_offset[directions[v4]]
                                                         + x
                                                         + x_offset[directions[v4]]]] )
          {
            putchar('!');
            fail_2();
          }
          if ( map_backup[y_offset[directions[v4]]][3005 * y + x_offset[directions[v4]] + x] == -3 )// map[y + y_offset][x + x_offset]
            --problem_solved;
          map[y_offset[directions[v4]]][3005 * y_offset[directions[v4]]
                                      + 3005 * y
                                      + x_offset[directions[v4]]
                                      + x
                                      + x_offset[directions[v4]]] = -1;// map[y + y_offset * 2][x + x_offset * 2]
          map[y_offset[directions[v4]]][3005 * y + x_offset[directions[v4]] + x] = -2;// map[y + y_offset][x + x_offset]
          map[y][x] = map_backup[y][x];
          y += y_offset[directions[v4]];
          x += x_offset[directions[v4]];
        }
      }
      else
      {
        if ( !is_composite[map[y_offset[directions[v4]]][3005 * y + x_offset[directions[v4]] + x]] )// map[y + y_offset][x + x_offset]
          fail_2();
        map[y_offset[directions[v4]]][3005 * y + x_offset[directions[v4]] + x] = -2;// map[y + y_offset][x + x_offset]
        v1 = y;
        v2 = x;
        map[v1][v2] = random_composite();
        y += y_offset[directions[v4]];
        x += x_offset[directions[v4]];
      }
      if ( problem_solved != problem_total )
      {
        null();
        goto LABEL_26;
      }
      return 1;
    }
    

init_primes 函数计算 3000 以内的质数，保存在数组中； set_map 函数随机生成一个 20 x 20 地图，存放在数组
`int[3005][3005]` map 与 map_backup
中,-1为箱子(Box)，-2为主角位置(Player)，-3为箱子的目标位置(Target)，质数为墙，合数为空地； print_gift
将地图的各个值输出，然后输入 wasd 移动，后面就是判断逻辑。

但是出题人写的逻辑与以前玩的推箱子逻辑有些差别（应该叫游戏 ~~bug~~ 特色），第一点比较容易看出来，就是 Player 不能移动到 Target
位置，否则这个 Target 就没了，不可能过关；另一点比较难发现，是在修改脚本已经解决了第一点后经常出现的，明明路径完全正确，却总在中途 `!fail`
了，调试了很久才发现，是 Player 踩在一个初始位置为 Box 的位置 (map_backup[pos] 为-1)
时，如果下一步推动箱子，脚下（原位置）就会凭空出现一个箱子，导致之后移动失败。

明白了这两点还不够，因为地图是随机生成的，有概率某个 Box 的生成位置卡在墙边导致无解，如下所示：

![](https://p5.ssl.qhimg.com/t01698e7ce77ecf6e81.png)

`$`代表 Box ，右边的`$`被卡住出不来，直接无解。

当然，有解的情况也不一定能解出来，这跟自动化推箱子脚本有关系，脚本写得差，跑脚本可能会很久，等跑出来早就 timeout 了。

写脚本这种事肯定是不会自己干的，直接 github 搜就完事了，找一个看起来实现比较简单的：

<https://github.com/adhikary97/Sokoban-AI-Solver>

还要阅读源码，将上面的两点限制加进去，也就是 Player 不能移动到 Target ，和Player 踩在一个初始为 Box 的位置时不能推动箱子。

脚本如下：

    
    
    #!/usr/bin/python2
    # coding=utf-8
    from pwn import *
    import traceback
    import os
    
    # context.log_level = 'debug'
    local = True
    
    '''
    def fail():
        print('fail.')
        exit(-1)
    
    map = [0] * 400
    size = 20
    # set map
    count = 0
    pos = 10 * size + 10
    while count < 4:
        move = 0
        # w a s d to move
        # move value in [1, -1, size, -size]
        if map[pos + move] == -1:
            if map[pos + move * 2] == -3:
                count += 1
                map[pos + move * 2] = -1
                map[pos] = map_backup[pos]
            else: # map[pos + move * 2] != -3 ->
                if map[pos + move * 2] is not composite:
                    fail()
                if map_backup[pos + move] == -3:
                    count--                map[pos + move * 2] = -1
                map[pos] = map_backup[pos]
        else: # map[pos + move] != -1 ->
            if map[pos + move] is not composite:
                fail()
            map[pos] = random_composite()
    
        map[pos + move] = -2
        pos = pos + move
    '''
    
    '''
    推箱子，地图规模 20 x 20 ，箱子数 4 ，每次随机生成
    合数为路，质数为墙， -1 为箱子， -3 为箱子目标位置
    '''
    def run():
        if local:
            p = process('./sycgame')
            # p = gdb.debug('./sycgame', 'b puts')
        else:
            p = remote('124.70.152.166', 1448)
    
        is_prime = [1] * 3005
        is_prime[1] = 0
        i = 2
        while i < 3000:
            if is_prime[i]:
                j = 2
                while j * i < 3005:
                    is_prime[j * i] = 0
                    j = j + 1
            i = i + 1
    
        # print(is_prime)
    
        size = 20
        def save_map_to_path(s, path):
            t = '#' * size + '\n'
            for y in range(1, size - 1):
                t += '#'
                for x in range(1, size - 1):
                    i = y * size + x
                    if s[i] == -2:
                        t += '@' # player
                    elif s[i] == -1:
                        t += '$' # Box
                    elif s[i] == -3:
                        t += '.' # Destination
                    else:
                        assert s[i] > 0
                        if is_prime[s[i]]:
                            t += '#' # wall
                        else:
                            t += ' ' # path
                t += '#\n'
            t += '#' * size + '\n'
            print(t)
            with open(path, 'w') as f:
                f.write('Level 1\n' + t)
    
        for i in range(5):
            print(i)
            p.sendlineafter('Ready?(Y/n):', 'Y')
            p.recvuntil('gift:\n')
            s = [int(j) for j in p.recvline().strip('\n ').split(' ')]
            # 试试 https://github.com/adhikary97/Sokoban-AI-Solver
            # 修改了一些约束条件
            '''
            7   ->
                    box_origin = []
            244 +
                    box_origin.append(coordinates())
                    # print(box_origin)
            288 ->
                    if self.map[x1][y1].wall or self.map[x1][y1].target or ((p[0], p[1]) in box_origin and (x1, y1) in s.boxes()):
            349 ->
                    if (x - 1, y) in box_pos and (x, y) not in box_origin:
            352, 355, 358相似
            363 ->
                    if not (matrix[x - 1][y].wall or matrix[x - 1][y].target) and (x - 1, y) not in box_pos and not matrix[x - 1][y].visited:
            365, 367, 369相似
            '''
            save_map_to_path(s, './levels.txt')
    
            path = os.popen('python3 ./Sokoban-AI-Solver-master/sokoban.py 1 a -t 1').readlines()[-1].strip('\n ').replace('d', 's').replace('r', 'd').replace('u', 'w').replace('l', 'a').replace(' ', '')
            print(path)
            if 'Timeaimit' in path:
                p.close()
                return -1
            p.sendline(path)
            if i == 4: break
            line = p.recvline().strip('\n')
            print(line)
            if 'fail' in line:
                p.close()
                return -1
    
        p.interactive()
        return 0
    
    while True:
        print('==============================================================================')
        if run() != -1:
            break
    

能连续跑完5轮概率比较小，可能很长时间才能跑通一次。而且可能由于输出缓冲的问题，我跑通了很多次都没拿到 flag
，本地完全没问题（被这个问题卡了很久），后来跟题目负责人沟通，他那儿跑出 flag 后发给我。

flag: SCTF{push_box_goooood_game}

###  SycOS

题目给了 risc-v 的 kernel, fs.img, sctf ，表明就是 risc-v 逆向， `README.md` 贴心的说用 qemu
，然后给个链接自己搜去。嗯…… qemu ，还是算了吧，懒得配环境，这不是给了程序吗，就硬逆。手上还没有能逆 risc-v 的 ida
，只好祭出去年安装后至今用过两次的 Ghidra 了。

sctf 拖入 Ghidra ，进入 entry ，一顿分析：

    
    
    ulonglong rand(void)
    
    {
      seed = seed * 1103515245 + 12345;
      return (seed << 33) >> 49;
    }
    
    
    void gift(void)
    
    {
      ulonglong uVar1;
      ulonglong uVar2;
      ulonglong uVar3;
      ulonglong uVar4;
    
      printf("gift:\n");
      seed = 0x1447aabb;
      uVar1 = rand();
      uVar2 = rand();
      uVar3 = rand();
      uVar4 = rand();
      printf("\t1.%x %x %x %x\n",uVar1,uVar2,uVar3,uVar4);
      printf("\t2.Fake Tea\n");
      printf("\t3.Based on xv6 2020 labs & util branch.\n");
      return;
    }
    
    void replace_mem0_index_with_mem1_15_sub_index(ulonglong index)
    
    {
      longlong i;
      longlong lVar1;
      byte buffer [256];
    
      buffer._0_8_ = 0;
      memset(buffer + 8,0,248);
      lVar1 = (longlong)((int)index << 8);
      memcpy(buffer,mem0 + lVar1,0x100);
      i = (longlong)((15 - (int)index) * 0x100);
      memcpy(mem0 + lVar1,mem1 + i,0x100);
      memcpy(mem1 + i,buffer,0x100);
      return;
    }
    
    void tea_decrypt_mem1(void)
    
    {
      longlong i;
      int sum;
      uint *mem1_ptr;
      uint v0;
      uint v1;
    
      i = 0;
      do {
        mem1_ptr = (uint *)(mem1 + i);
        v0 = *mem1_ptr;
        v1 = mem1_ptr[1];
        sum = 0;
        do {
          v1 = v1 - (v0 * 16 + k2 ^ (v0 >> 5) + k3 ^ v0 + sum);
          v0 = v0 - (v1 + sum ^ v1 * 0x10 + k0 ^ (v1 >> 5) + k1);
          sum = sum + -0x61c88647;
        } while (sum != -0xe443238);
        *mem1_ptr = v0;
        mem1_ptr[1] = v1;
        i = i + 8;
      } while (i != 0x1000);
      return;
    }
    
    void tea_encrypt_mem0(void)
    
    {
      longlong i;
      int sum;
      uint *mem0_ptr;
      uint v1;
      uint v0;
    
      i = 0;
      do {
        mem0_ptr = (uint *)(mem0 + i);
        v0 = *mem0_ptr;
        v1 = mem0_ptr[1];
        sum = 0;
        do {
          sum = sum + -0x61c88647;
          v0 = (v1 * 16 + k0 ^ (v1 >> 5) + k1 ^ sum + v1) + v0;
          v1 = v1 + (v0 + sum ^ v0 * 16 + k2 ^ (v0 >> 5) + k3);
        } while (sum != -0x1c886470);
        *mem0_ptr = v0;
        mem0_ptr[1] = v1;
        i = i + 8;
      } while (i != 0x1000);
      return;
    }
    
    void change_mem0_mem1(void)
    
    {
      ulonglong i;
    
      i = 0;
      do {
        tea_encrypt_mem0();
        tea_decrypt_mem1();
        replace_mem0_index_with_mem1_15_sub_index(i);
        FUN_0000091a(mem0,mem1);
        i = SEXT48((int)i + 1);
      } while (i != 16);
      return;
    }
    
    void set_mem_with_input(char *input)
    
    {
      longlong j;
      ulonglong value;
      longlong end;
      longlong input_index;
      longlong start;
    
      mem0 = (char *)malloc(0x1000);
      mem1 = (char *)malloc(0x1000);
      memset(mem0,0,0x1000);
      memset(mem1,0,0x1000);
      end = 128;
      start = 0;
      input_index = 0;
      do {
        seed = (longlong)(int)((uint)(byte)input[input_index] + (int)input_index) & 0xffffffff;
        j = start;
        do {
          value = rand();
          mem0[j] = (char)value;
          j = j + 1;
        } while (j != end);
        input_index = input_index + 1;
        start = start + 0x80;
        end = end + 0x80;
      } while (input_index != 32);
      end = 0x80;
      start = 0;
      input_index = 0;
      do {
        seed = (longlong)(int)((uint)(byte)input[input_index + 0x20] + (int)input_index) & 0xffffffff;
        j = start;
        do {
          value = rand();
          mem1[j] = (char)value;
          j = j + 1;
        } while (j != end);
        input_index = input_index + 1;
        start = start + 0x80;
        end = end + 0x80;
      } while (input_index != 0x20);
      return;
    }
    
    void entry(void)
    
    {
      int input_len;
      ulonglong uVar1;
      char input [256];
    
      printf("Welcome SCTF2021! The new xv6 lab designed by P****OS\ncan you solve this ?\ninput:");
      gift();
      read_str(input,256);
      input_len = strlen(input);
      input[(longlong)(input_len + -1) & 0xffffffff] = '\0';
      input_len = strlen(input);
      if (input_len != 64) {
        printf("fail!\n");
                        /* WARNING: Subroutine does not return */
        exit(0);
      }
      set_mem_with_input(input);
      change_mem0_mem1();
      uVar1 = memcmp(mem0,&DAT_00001ec8,0x1000);
      if ((uVar1 == 0) && (uVar1 = memcmp(mem1,&DAT_00000ec8,0x1000), uVar1 == 0)) {
        printf("yes,you are right.!\n");
                        /* WARNING: Subroutine does not return */
        exit(0);
      }
      printf("fail! Try!");
                        /* WARNING: Subroutine does not return */
      exit(0);
    }
    

gift 函数输出几个伪随机数，都是固定值；还有 Fake Tea ，最初不知道是什么，等分析完后才知道说的是魔改 tea 加密。

大部分都恢复出来了，一些函数（如 exit, malloc ）跟入是 ecall 系统调用，是根据逻辑猜测得到的。只剩下一个函数， FUN_0000091a
，跟入是序号 22 的系统调用，不知道做什么。

sctf 就这些，然后要找系统调用，又得分析 kernel 。同样拖入 Ghidra ，但是不好找关键位置，这时候得祭出 strings
大法：`strings ./kernel`，找到关键点：

    
    
    ...
    argraw
    %d %s: unknown sys call %d
    bcache
    buffer
    bget: no buffers
    bwrite
    brelse
    freeing free block
    balloc: out of blocks
    bmap: out of range
    iget: no inodes
    invalid file system
    icache
    inode
    ialloc: no inodes
    ...
    

有个`%d %s: unknown sys call %d`，正是系统调用的报错信息， Ghidra 里找到 0x800083f0
，查看引用，找到关键位置：

    
    
    void FUN_80002b0c(void)
    
    {
      int iVar1;
      longlong lVar2;
      undefined8 uVar3;
      longlong lVar4;
    
      lVar2 = FUN_800019de();
      lVar4 = *(longlong *)(lVar2 + 0x58);
      iVar1 = (int)*(undefined8 *)(lVar4 + 0xa8);
      if ((iVar1 - 1U < 0x16) && (*(code **)(&DAT_80008428 + (longlong)iVar1 * 8) != (code *)0x0)) {
        uVar3 = (**(code **)(&DAT_80008428 + (longlong)iVar1 * 8))();
        *(undefined8 *)(lVar4 + 0x70) = uVar3;
        return;
      }
      printk("%d %s: unknown sys call %d\n");
      *(undefined8 *)(*(longlong *)(lVar2 + 0x58) + 0x70) = 0xffffffffffffffff;
      return;
    }
    

所以系统调用表在 0x80008428 ，需要的22号调用就是 0x80008428 + 22 * 8 = 0x800084d8 ，找到函数
FUN_800060c6

    
    
    undefined8 FUN_800060c6(void)
    
    {
      undefined8 uVar1;
      undefined8 *puVar2;
      undefined8 *puVar3;
      ulonglong uVar4;
      longlong lVar5;
      char *mem1;
      char *mem0;
      undefined8 *puStack56;
    
      FUN_80000c10(&DAT_800250a8);
      uVar4 = (ulonglong)DAT_80025020;
      if (((*(ushort *)(DAT_80025010 + 2) ^ DAT_80025020) & 7) != 0) {
        do {
          lVar5 = (longlong)*(int *)(uVar4 * 8 + DAT_80025010 + 4);
          if ((&DAT_80023030)[(lVar5 + 0x200) * 0x10] != '\0') {
            panic("virtio_disk_intr status");
            puStack56 = &DAT_80025000;
            lVar5 = get_ecall_arg_to_memory64(0,(longlong *)&mem0);
            uVar1 = 0xffffffffffffffff;
            if (-1 < lVar5) {
              lVar5 = get_ecall_arg_to_memory64(1,(longlong *)&mem1);
              uVar1 = 0xffffffffffffffff;
              if (-1 < lVar5) {
                lVar5 = FUN_800019de();
                puVar2 = (undefined8 *)FUN_80000ff8(*(undefined8 *)(lVar5 + 0x50),mem0,0);
                lVar5 = FUN_800019de();
                puVar3 = (undefined8 *)FUN_80000ff8(*(undefined8 *)(lVar5 + 0x50),mem1,0);
                uVar1 = *puVar2;
                *puVar2 = *puVar3;
                *puVar3 = uVar1;
                sfence.vma(0,0);
                uVar1 = 1;
              }
            }
            return uVar1;
          }
          lVar5 = (lVar5 + 0x200) * 0x10;
          *(undefined4 *)(*(longlong *)(&DAT_80023028 + lVar5) + 4) = 0;
          FUN_80002370(*(undefined8 *)(&DAT_80023028 + lVar5));
          uVar4 = (longlong)(int)(DAT_80025020 + 1) & 7;
          DAT_80025020 = (ushort)uVar4;
        } while (((ulonglong)*(ushort *)(DAT_80025010 + 2) & 7) != uVar4);
      }
      _DAT_10001064 = _DAT_10001060 & 3;
      uVar1 = FUN_80000cc4(&DAT_800250a8);
      return uVar1;
    }
    

关键在于中间的两次 FUN_80000ff8 ，再跟入就什么都看不懂了，不过后面是一个交换，猜测下应该是将 mem0 和 mem1
内存交换了，尝试了下还真是。

编写逆向程序：

    
    
    // clear && gcc ./main.c && ./a.out
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <unistd.h>
    #include <sys/mman.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/fcntl.h>
    #include <assert.h>
    
    char* mem0;
    char* mem1;
    unsigned int k0 = 0x11222233, k1 = 0xAABBCCDD, k2 = 0x1A2B3C4D, k3 = 0xCC1122AA;
    typedef unsigned long long ulonglong;
    typedef long long longlong;
    typedef char byte;
    typedef unsigned int uint;
    
    void replace_mem0_index_with_mem1_15_sub_index_inv(ulonglong index) {
        longlong i;
        longlong lVar1;
        byte buffer [256];
    
        memset(buffer, 0, 256);
        lVar1 = index << 8;
        i = (15 - index) * 0x100;
        memcpy(buffer,mem1 + i,0x100);
        memcpy(mem1 + i,mem0 + lVar1,0x100);
        memcpy(mem0 + lVar1,buffer,0x100);
        return;
    }
    
    void tea_decrypt_mem1_inv(void) {
        longlong i;
        int sum;
        uint *mem1_ptr;
        uint v0;
        uint v1;
    
        i = 0;
        do {
            mem1_ptr = (uint *)(mem1 + i);
            v0 = *mem1_ptr;
            v1 = mem1_ptr[1];
            sum = -0xe443238;
            do {
                sum = sum - -0x61c88647;
                v0 += (v1 + sum) ^ ((v1 << 4) + k0) ^ ((v1 >> 5) + k1);
                v1 += ((v0 << 4) + k2) ^ ((v0 >> 5) + k3) ^ (v0 + sum);
            } while (sum != 0);
            *mem1_ptr = v0;
            mem1_ptr[1] = v1;
            i = i + 8;
        } while (i != 0x1000);
        return;
    }
    
    void tea_encrypt_mem0_inv(void) {
        longlong i;
        int sum;
        uint *mem0_ptr;
        uint v1;
        uint v0;
    
        i = 0;
        do {
            mem0_ptr = (uint *)(mem0 + i);
            v0 = *mem0_ptr;
            v1 = mem0_ptr[1];
            sum = -0x1c886470;
            do {
                v1 -= (v0 + sum) ^ ((v0 << 4) + k2) ^ ((v0 >> 5) + k3);
                v0 -= ((v1 << 4) + k0) ^ ((v1 >> 5) + k1) ^ (sum + v1);
                sum = sum - -0x61c88647;
            } while (sum != 0);
            *mem0_ptr = v0;
            mem0_ptr[1] = v1;
            i = i + 8;
        } while (i != 0x1000);
        return;
    }
    
    ulonglong seed;
    void _srand(ulonglong _seed) {
        seed = _seed;
    }
    
    uint _rand() {
        seed = seed * 1103515245 + 12345;
        return (seed << 33) >> 49;
    }
    
    int main() {
        struct stat sb;
        mem0 = (char*) malloc(0x1000);
        mem1 = (char*) malloc(0x1000);
        if (mem0 == NULL || mem1 == NULL) {
            perror("malloc");
            exit(-1);
        }
    
        /*
        char input[65] = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        puts(input);
    
        for (int i = 0; i < 32; i++) {
            srand(input[i] + i);
            for (int j = 128 * i; j < 128 * i + 128; j++) {
                mem0[j] = rand();
            }
        }
        for (int i = 0; i < 32; i++) {
            srand(input[i + 32] + i);
            for (int j = 128 * i; j < 128 * i + 128; j++) {
                mem1[j] = rand();
            }
        }
    
        for (int i = 0; i < 16; i++) {
            tea_encrypt_mem0();
            tea_decrypt_mem1();
            replace_mem0_index_with_mem1_15_sub_index();
        }
    
        /**/
    
        int fd = open("./sctf", O_RDONLY);
        if (fd < 0) {
            perror("open");
            exit(-1);
        }
    
        if (fstat(fd, &sb) == -1) {
            perror("fstat");
            exit(-1);
        }
    
        unsigned char* mapped = (char*) mmap(0, sb.st_size, PROT_READ, MAP_SHARED, fd, 0);
        if (mapped == (unsigned char*) -1) {
            perror("mmap");
            exit(-1);
        }
    
        memcpy(mem0, mapped + 0x1F78, 0x1000);
        memcpy(mem1, mapped + 0xF78, 0x1000);
        assert(mem0[0] == 0x29 && mem0[1] == 0x3A);
    
        if (munmap(mapped, sb.st_size) == -1) {
            perror("munmap");
            exit(-1);
        }
    
        for (int i = 15; i >= 0; i--) {
            // FUN_0000091a_inv(mem0, mem1);
    
            char* temp = mem0;
            mem0 = mem1;
            mem1 = temp;
            /**/
            replace_mem0_index_with_mem1_15_sub_index_inv(i);
            tea_decrypt_mem1_inv();
            tea_encrypt_mem0_inv();
        }
    
        /*
        for (int i = 0; i < 32; i++) {
            printf("0x%02x, ", mem0[i] & 0xff);
            if ((i + 1) % 16 == 0) putchar('\n');
        }
    
        putchar('\n');
    
        /*
        _srand('S');
        for (int i = 0; i < 32; i++) {
            printf("0x%02x, ", _rand() & 0xff);
            if ((i + 1) % 16 == 0) putchar('\n');
        }
        putchar('\n');
        /**/
        for (int i = 0; i < 32; i++) {
            for (int j = 0; j < 128; j++) {
                _srand(j + i);
                for (int k = 0; k < 128; k++)
                    if ((_rand() & 0xff) != (mem0[k + 128 * i] & 0xff))
                        goto continue_search;
                putchar(j);
                goto scan_next;
    
                continue_search:
                ;
            }
            printf("\nNot Found.\n");
            goto finish;
            scan_next:
            ;
        }
    
        for (int i = 0; i < 32; i++) {
            for (int j = 0; j < 128; j++) {
                _srand(j + i);
                for (int k = 0; k < 128; k++)
                    if ((_rand() & 0xff) != (mem1[k + 128 * i] & 0xff))
                        goto continue_search1;
                putchar(j);
                goto scan_next1;
    
                continue_search1:
                ;
            }
            printf("\nNot Found.\n");
            goto finish;
            scan_next1:
            ;
        }
        finish:
        putchar('\n');
        /**/
        free(mem0);
        free(mem1);
        return 0;
    }
    

flag: SCTF{xv6_nice_lab_6666_YOU_ARE_6666666_OrzzzzzzzzzzzzzrO_wowowo}

###  godness dance

跟其它几道题目比起来，这道题就像是来搞笑的。。。

main 前半部分：

    
    
      __printf_chk(1, "Input:");
      do
      {
        v5 = v4++;
        __isoc99_scanf("%c", v5);
      }
      while ( v4 != v14 );
      v6 = input;
      do
      {
        v7 = *v6++;
        ++count_src[v7 - 'a'];
      }
      while ( v6 != v14 );
      for ( i = 0LL; i != 26; ++i )
      {
        if ( count_src[i] != count_dst[i] )
          CountWrong();
      }
    

输入 28 个字符 [a-z] ，统计字符个数，除了 i 和 u 是 2 个，其余都是 1 个。

main 后半部分：

    
    
      sub_1400(&v12, 28u, 200);
      for ( j = 1LL; j != 29; ++j )
      {
        if ( count_sort_result_index[j] != dword_4020[j] )
          Wrong();
      }
    

sub_1400 前部分：

    
    
      v3 = _200;
      v4 = _28;
      if ( _200 >= 0 )
        memset(input_count_sum, 0, 4LL * _200 + 4);
      if ( (int)_28 <= 0 )
      {
        if ( v3 <= 0 )
          return;
    LABEL_7:
        v7 = input_count_sum[0];
        v8 = 1LL;
        do
        {
          v7 += input_count_sum[v8];
          input_count_sum[v8++] = v7;
        }
        while ( v3 >= (int)v8 );
        if ( (int)_28 <= 0 )
          return;
        goto LABEL_10;
      }
      v5 = 1LL;
      do
      {
        v6 = input_sub_1[v5];
        input_buffer[v5++] = v6;
        ++input_count_sum[v6];
      }
      while ( _28 - 1 + 2LL != v5 );
      if ( v3 > 0 )
        goto LABEL_7;
    LABEL_10:
      v9 = (int)_28;
      do
      {
        v10 = input_buffer[v9];
        v11 = input_count_sum[v10];
        count_sort_result_index[v11] = v9--;
        input_count_sum[v10] = v11 - 1;
      }
      while ( (int)v9 > 0 );
    

学过算法的话跟着流程走一遍就知道是计数排序，计算的 count_sort_result_index
是排好序后数在原数组中的下标。而且动调一下，发现后面部分没有修改 count_sort_result_index ，很简单：

    
    
    index = [2, 26, 17, 28, 24, 11, 21, 10, 16, 20, 19, 18, 3, 8, 6, 12, 9, 14, 13, 22, 4, 27, 15, 23, 1, 25, 7, 5]
    index = [i - 1 for i in index]
    s = 'abcdefghiijklmnopqrstuuvwxyz'
    t = [0] * 28
    for i in range(len(index)):
        t[index[i]] = s[i]
    print(''.join(t))
    # waltznymphforquickjigsvexbud
    

###  CplusExceptionEncrypt

这道题是利用 C++ 的异常处理控制执行流程，问题在于 F5 后的代码只会解析到 throw 抛异常，后面的处理看不到。

    
    
      printf("---------------------Welcome_to_SCTF_2021---------------------\n");
      printf("Please input your flag: \n");
      scanf("%s", data);
      length = strlen(data);
      if ( length == 32 )
      {
        w = 0;
        v0 = *(_DWORD *)data;
        v1 = *(_DWORD *)&data[4];
        v2 = *(_DWORD *)&data[8];
        v3 = *(_DWORD *)&data[12];
        sum1 = 0;
        sum2 = 0;
        rbx3 = _cxa_allocate_exception(0x20ui64);
        std::allocator<char>::allocator(&v8);
        std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string(rbx3, "init_part", &v8);
        std::allocator<char>::~allocator(&v8);
        _cxa_throw(
          rbx3,
          (struct type_info *)&`typeinfo for'std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>,
          refptr__ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED1Ev);
      }
      printf("length error!\n");
    

这个时候就想怎么能将整个流程恢复出来，让 F5 能正常解析，一个很自然的想法就是修改指令，修改 throw 为 jmp ，就找 throw 对应的
catch 段，这里的很容易找，在 ida Graph View 里可以清晰看到：

![](https://p4.ssl.qhimg.com/t01ba078bf44f2307e7.png)

（也有可能看到的不是这样的，而是 call cxa_throw 这条指令与上面的块合在一起，并且没有指向 catch 块的箭头，暂不知道具体原因，可能是
ida 的问题，关闭 ida 保存到 i64 后重新打开就没了。这种情况下可以删除 i64 或者重命名，让ida打开时重新开始解析 exe
，这样就能看到了）

catch 段的 rdx 应该是表明由哪个 catch 块处理，这里只有一个，就应该是直接跳转到 loc_402A5F 进行处理， patch 为 jmp
：

![](https://p1.ssl.qhimg.com/t01f6d4b49759f9303e.png)

再 F5 ，这里的处理解析出来了：

    
    
      printf("---------------------Welcome_to_SCTF_2021---------------------\n");
      printf("Please input your flag: \n");
      scanf("%s", data);
      length = strlen(data);
      if ( length == 32 )
      {
        w = 0;
        inp[0] = *(_DWORD *)data;
        inp[1] = *(_DWORD *)&data[4];
        inp[2] = *(_DWORD *)&data[8];
        inp[3] = *(_DWORD *)&data[12];
        v0 = *(_DWORD *)data;
        v1 = *(_DWORD *)&data[4];
        v2 = *(_DWORD *)&data[8];
        v3 = *(_DWORD *)&data[12];
        sum1 = 0;
        sum2 = 0;
        *(_QWORD *)dst = 0i64;
        *(_QWORD *)&dst[2] = 0i64;
        *(_QWORD *)out1 = 0i64;
        *(_QWORD *)&out1[8] = 0i64;
        rbx3 = _cxa_allocate_exception(0x20ui64);
        std::allocator<char>::allocator(&v18);
        std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string(rbx3, "init_part", &v18);
        std::allocator<char>::~allocator(&v18);
        v9 = _cxa_get_exception_ptr(rbx3);
        std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string(&init, v9);
        _cxa_begin_catch(rbx3);
        qmemcpy(key, "Welcome_to_sctf!", sizeof(key));
        k0_0 = *(_DWORD *)key;
        k1_0 = *(_DWORD *)&key[4];
        k2_0 = *(_DWORD *)&key[8];
        k3_0 = *(_DWORD *)&key[12];
        /*
        set cmp_arr
        /**/
        std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string(&init);
        _cxa_end_catch();
        for ( i = 0; i <= 31; ++i )
        {
          cnt = 0;
          srand(0x53435446u);
          do
          {
            control1 = rand();
            switch ( control1 )
            {
              case 0x5208:
                v6 = (struct_of_step3 *)_cxa_allocate_exception(1ui64);
                struct_of_step3::struct_of_step3(v6);
                _cxa_throw(v6, (struct type_info *)&`typeinfo for'struct_of_step3, 0i64);
              case 0x6591:
                v4 = (struct_of_step1 *)_cxa_allocate_exception(1ui64);
                struct_of_step1::struct_of_step1(v4);
                _cxa_throw(v4, (struct type_info *)&`typeinfo for'struct_of_step1, 0i64);
              case 0x10A9:
                v5 = (struct_of_step2 *)_cxa_allocate_exception(1ui64);
                struct_of_step2::struct_of_step2(v5);
                _cxa_throw(v5, (struct type_info *)&`typeinfo for'struct_of_step2, 0i64);
            }
            ++cnt;
          }
          while ( cnt != 3 );
        }
        v7 = (last_struct *)_cxa_allocate_exception(1ui64);
        text_84(v7);
        _cxa_throw(v7, (struct type_info *)&`typeinfo for'last_struct, 0i64);
      }
      printf("length error!\n");
      return 0;
    }
    

效果不错，美中不足的就是前面还留下了一些 exception 相关的函数，都是没用的。这些并不影响分析流程，也就不管了。

继续分析，中间有 srand ，那么 rand 生成的数是完全可预测的，写个程序跑一下就得到了（动调也可以），然后又要处理三个 throw ， Graph
View 里看，很不幸，第一个 case 0x5208: 的 throw 块就没有了指向 catch 块的箭头，这就得手动找一下。

![](https://p3.ssl.qhimg.com/t01f368d2bc82672987.png)

这里有一个 starts at 40273D ，也就是说 try 块是从 0x40273D 开始的，而相应的 catch 块也会有这样的标识，鼠标点下
40273D 使其高亮，然后拖动图在周围找一下高亮，定位到 catch 块：

![](https://p5.ssl.qhimg.com/t0100df3740702885da.png)

可以看到这个 catch 块有多个标识： owned by 40273D ，说明有多个 catch 块，而继续定位另两个 case 的 throw
指令，发现指向这块的 throw 正是 case 0x6591 的 throw 块，或许第一个 case 的 throw 没有箭头指向 catch
就是因为有一个 throw 占用了这个箭头。。。

多个 catch 的分发器，由 rdx 的值决定分发给哪个 catch 块，至于 rdx 的值与 catch
块的对应关系，这个暂时还不知道，可能是程序启动时由某个函数注册的吧。要确定上面三个 throw 到这里 catch 块的 rdx 的值，通过动调就可以。

后面的大部分也还是上面的异常处理隐藏流程， patch 为 jmp 就都能恢复了，整体恢复出来如下：

    
    
      printf("---------------------Welcome_to_SCTF_2021---------------------\n");
      printf("Please input your flag: \n");
      scanf("%s", data);
      length = strlen(data);
      if ( length == 32 )
      {
        for ( w = 0; w <= 1; ++w )
        {
          if ( !w )
          {
            inp[0] = *(_DWORD *)data;
            inp[1] = *(_DWORD *)&data[4];
            inp[2] = *(_DWORD *)&data[8];
            inp[3] = *(_DWORD *)&data[12];
          }
          if ( w == 1 )
          {
            inp[0] = *(_DWORD *)&data[16];
            inp[1] = *(_DWORD *)&data[20];
            inp[2] = *(_DWORD *)&data[24];
            inp[3] = *(_DWORD *)&data[28];
          }
          v0 = inp[0];
          v1 = inp[1];
          v2 = inp[2];
          v3 = inp[3];
          sum1 = 0;
          sum2 = 0;
          *(_QWORD *)dst = 0i64;
          *(_QWORD *)&dst[2] = 0i64;
          *(_QWORD *)out1 = 0i64;
          *(_QWORD *)&out1[8] = 0i64;
          rbx9 = _cxa_allocate_exception(0x20ui64);
          std::allocator<char>::allocator(&v62);
          std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string(
            rbx9,
            "init_part",
            &v62);
          std::allocator<char>::~allocator(&v62);
          v13 = _cxa_get_exception_ptr(rbx9);
          std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string(&init, v13);
          _cxa_begin_catch(rbx9);
          qmemcpy(key, "Welcome_to_sctf!", sizeof(key));
          k0_0 = *(_DWORD *)key;
          k1_0 = *(_DWORD *)&key[4];
          k2_0 = *(_DWORD *)&key[8];
          k3_0 = *(_DWORD *)&key[12];
          /*
           set cmp_arr
          /**/
          std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string(&init);
          _cxa_end_catch();
          for ( i = 0; i <= 31; ++i )
          {
            cnt = 0;
            srand(0x53435446u);
            do
            {
              control1 = rand();                    // 0x6591
                                                    // 0x10A9
                                                    // 0x5208
                                                    // 0x4be2
              switch ( control1 )
              {
                case 0x5208:                        // 2
                  v6 = (struct_of_step3 *)_cxa_allocate_exception(1ui64);
                  struct_of_step3::struct_of_step3(v6);
                  _cxa_begin_catch(v32);
                  v33 = add(sum1, i);
                  v34 = shr_5(v0);
                  v35 = add(v34, k1_0);
                  v36 = add(v0, sum1);
                  v37 = shl_4(v0);
                  v38 = add(v37, k0_0);
                  v39 = xor(v38, v36);
                  v40 = xor(v39, v35);
                  v1 += xor(v40, v33);
                  v41 = add(sum2, i);
                  v42 = shr_5(v2);
                  v43 = add(v42, k1_0);
                  v44 = add(v2, sum1);
                  v45 = shl_4(v2);
                  v46 = add(v45, k0_0);
                  v47 = xor(v46, v44);
                  v48 = xor(v47, v43);
                  v3 += xor(v48, v41);
                  _cxa_end_catch();
                  break;
                case 0x6591:                        // 0
                  v4 = (struct_of_step1 *)_cxa_allocate_exception(1ui64);
                  struct_of_step1::struct_of_step1(v4);
                  _cxa_begin_catch(v14);
                  sum1 = add(sum1, delta);
                  sum2 = add(sum2, delta);
                  _cxa_end_catch();
                  break;
                case 0x10A9:                        // 1
                  v5 = (struct_of_step2 *)_cxa_allocate_exception(1ui64);
                  struct_of_step2::struct_of_step2(v5);
                  _cxa_begin_catch(v15);
                  v16 = add(sum1, i);
                  v17 = shr_5(v1);
                  v18 = add(v17, k3_0);
                  v19 = add(v1, sum1);
                  v20 = shl_4(v1);
                  v21 = add(v20, k2_0);
                  v22 = xor(v21, v19);
                  v23 = xor(v22, v18);
                  v0 += xor(v23, v16);
                  v24 = add(sum2, i);
                  v25 = shr_5(v3);
                  v26 = add(v25, k3_0);
                  v27 = add(v3, sum2);
                  v28 = shl_4(v3);
                  v29 = add(v28, k2_0);
                  v30 = xor(v29, v27);
                  v31 = xor(v30, v26);
                  v2 += xor(v31, v24);
                  _cxa_end_catch();
                  break;
              }
              ++cnt;
            }
            while ( cnt != 3 );
          }
          v7 = (last_struct *)_cxa_allocate_exception(1ui64);
          text_84(v7);
          _cxa_begin_catch(v49);
          dst[0] = v0 ^ HIBYTE(delta);
          dst[1] = v1 ^ BYTE2(delta);
          dst[2] = v2 ^ BYTE1(delta);
          dst[3] = v3 ^ (unsigned __int8)delta;
          _cxa_end_catch();
          m = 0;
          for ( j = 0; j <= 3; ++j )
          {
            for ( k = 0; k <= 3; ++k )
              out1[m++] = *((_BYTE *)&dst[j] + k);
          }
          x = 0;
          srand(0x53435446u);
          while ( x != 2 )
          {
            v8 = rand();                            // 0x6591
                                                    // 0x10A9
                                                    // 0x5208
                                                    // 0x4be2
            if ( v8 == 0x10A9 )                     // 1
            {
              v11 = (enc_next_struct *)_cxa_allocate_exception(0x18ui64);
              temp_4 = *enc_next_struct::enc_next_struct(v11, (uint8_t *)&init, out1, ciphertext);
              _cxa_begin_catch(v11);
              enc_next(temp_4.ourroundkeys, temp_4.ourplaintext, temp_4.ourciphertext);
              _cxa_end_catch();
            }
            else if ( v8 == 0x6591 )                // 0
            {
              v9 = (enc_next_ready_struct *)_cxa_allocate_exception(0x10ui64);
              v10 = enc_next_ready_struct::enc_next_ready_struct(v9, key, (uint8_t *)&init);
              v50 = v10->ourroundkeys;
              temp_3.ourciphertext = v10->ourciphertext;
              temp_3.ourroundkeys = v50;
              _cxa_begin_catch(v9);
              enc_next_ready(temp_3.ourciphertext, temp_3.ourroundkeys);
              _cxa_end_catch();
            }
            ++x;
          }
          if ( !w )
          {
            for ( i_0 = 0; i_0 <= 15; ++i_0 )
              encdata[i_0] = ciphertext[i_0];
          }
          if ( w == 1 )
          {
            for ( i_1 = 0; i_1 <= 15; ++i_1 )
              encdata[i_1 + 16] = ciphertext[i_1];
          }
        }
        for ( j_0 = 0; j_0 <= 31; ++j_0 )
        {
          if ( encdata[j_0] != cmp_arr[j_0] )
          {
            printf("Sorry!Your flag is wrong!!!!\n");
            exit(0);
          }
        }
        printf("\ncongratulations!!!!your flag is \nSCTF{%s}", data);
      }
      else
      {
        printf("length error!\n");
      }
      return 0;
    

enc_next_ready 与 enc_next 如下：

    
    
    void __cdecl enc_next(uint8_t *roundkeys, uint8_t *plaintext, uint8_t *ciphertext)
    {
      void *v3; // rbx
      _DWORD *v4; // rax
      uint8_t *v5; // rax
      uint8_t *v6; // rax
      void *v7; // rax
      uint8_t *v8; // rax
      std::__cxx11::string temp_2; // [rsp+20h] [rbp-60h] BYREF
      uint8_t tmp[16]; // [rsp+40h] [rbp-40h] BYREF
      char v11; // [rsp+5Eh] [rbp-22h] BYREF
      uint8_t t; // [rsp+5Fh] [rbp-21h]
      double temp_1; // [rsp+60h] [rbp-20h]
      int temp_0; // [rsp+6Ch] [rbp-14h]
      char temp; // [rsp+73h] [rbp-Dh]
      int a; // [rsp+74h] [rbp-Ch]
      int cnt; // [rsp+78h] [rbp-8h]
      uint8_t j; // [rsp+7Eh] [rbp-2h]
      uint8_t i; // [rsp+7Fh] [rbp-1h]
    
      v4 = _cxa_allocate_exception(4ui64);
      *v4 = 1;
      a = *(_DWORD *)_cxa_begin_catch(v4);
      for ( i = 0; i <= 15u; ++i )
      {
        v6 = roundkeys++;
        ciphertext[i] = *v6 ^ plaintext[i] ^ 0x66;
      }
      _cxa_end_catch();
      j = 1;
    LABEL_2:
      if ( j <= 9u )
      {
        for ( cnt = 0; ; ++cnt )
        {
          if ( cnt == 4 )
          {
            ++j;
            goto LABEL_2;
          }
          if ( cnt == 1 )
          {
            *(_DWORD *)_cxa_allocate_exception(4ui64) = 666;
            temp_0 = *(_DWORD *)_cxa_begin_catch(v3);
            inv_shift_rows(tmp);
            _cxa_end_catch();
            continue;
          }
          if ( cnt > 1 )
          {
            if ( cnt == 2 )
            {
              *(_QWORD *)_cxa_allocate_exception(8ui64) = 0x4050AA3D70A3D70Ai64;
              temp_1 = *(double *)_cxa_begin_catch(v3);
              for ( i = 0; i <= 0xFu; i += 4 )
              {
                t = tmp[i + 2] ^ tmp[i + 1] ^ tmp[i] ^ tmp[i + 3];
                ciphertext[i] = t ^ tmp[i] ^ mul2(tmp[i] ^ tmp[i + 1]);
                ciphertext[i + 1] = t ^ tmp[i + 1] ^ mul2(tmp[i + 1] ^ tmp[i + 2]);
                ciphertext[i + 2] = t ^ tmp[i + 2] ^ mul2(tmp[i + 2] ^ tmp[i + 3]);
                ciphertext[i + 3] = t ^ tmp[i + 3] ^ mul2(tmp[i + 3] ^ tmp[i]);
              }
              goto LABEL_29;
            }
            if ( cnt == 3 )
            {
              v3 = _cxa_allocate_exception(0x20ui64);
              std::allocator<char>::allocator(&v11);
              std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string(
                v3,
                "66666\n",
                &v11);
              std::allocator<char>::~allocator(&v11);
              v7 = _cxa_get_exception_ptr(v3);
              std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string(&temp_2, v7);
              _cxa_begin_catch(v3);
              for ( i = 0; i <= 15u; ++i )
              {
                v8 = roundkeys++;
                ciphertext[i] ^= *v8;
              }
              std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string(&temp_2);
              _cxa_end_catch();
            }
          }
          else if ( !cnt )
          {
            *(_BYTE *)_cxa_allocate_exception(1ui64) = '6';
            temp = *(_BYTE *)_cxa_begin_catch(v3);
            for ( i = 0; i <= 15u; ++i )
              tmp[i] = INV_S[ciphertext[i]];
    LABEL_29:
            _cxa_end_catch();
            continue;
          }
        }
      }
      for ( i = 0; i <= 15u; ++i )
        ciphertext[i] = S[ciphertext[i]];
      shift_rows(ciphertext);
      for ( i = 0; i <= 0xFu; ++i )
      {
        v5 = roundkeys++;
        ciphertext[i] ^= *v5;
      }
    }
    
    void __cdecl enc_next_ready(uint8_t *key, uint8_t *roundkeys)
    {
      uint8_t *v2; // rdx
      uint8_t *v3; // rax
      char *v4; // rax
      char v5; // r8
      char v6; // cl
      uint8_t *v7; // rax
      uint8_t temp_1; // [rsp+5h] [rbp-1Bh]
      uint8_t temp_2; // [rsp+6h] [rbp-1Ah]
      uint8_t temp_3; // [rsp+7h] [rbp-19h]
      uint8_t i; // [rsp+17h] [rbp-9h]
      uint8_t ia; // [rsp+17h] [rbp-9h]
      uint8_t *last4bytes; // [rsp+18h] [rbp-8h]
    
      for ( i = 0; i <= 15u; ++i )
      {
        v2 = key++;
        v3 = roundkeys++;
        *v3 = *v2;
      }
      last4bytes = roundkeys - 4;
      for ( ia = 0; ia <= 9u; ++ia )
      {
        temp_3 = S[*last4bytes];
        temp_1 = S[last4bytes[2]];
        temp_2 = S[last4bytes[3]];
        *roundkeys = *(roundkeys - 16) ^ S[last4bytes[1]] ^ RC[ia];
        roundkeys[1] = *(roundkeys - 15) ^ temp_1;
        roundkeys[2] = *(roundkeys - 14) ^ temp_2;
        roundkeys[3] = *(roundkeys - 13) ^ temp_3;
        roundkeys[4] = *(roundkeys - 12) ^ last4bytes[4];
        roundkeys[5] = *(roundkeys - 11) ^ last4bytes[5];
        roundkeys[6] = *(roundkeys - 10) ^ last4bytes[6];
        roundkeys[7] = *(roundkeys - 9) ^ last4bytes[7];
        roundkeys[8] = *(roundkeys - 8) ^ last4bytes[8];
        roundkeys[9] = *(roundkeys - 7) ^ last4bytes[9];
        roundkeys[10] = *(roundkeys - 6) ^ last4bytes[10];
        roundkeys[11] = *(roundkeys - 5) ^ last4bytes[11];
        roundkeys[12] = *(roundkeys - 4) ^ last4bytes[12];
        roundkeys[13] = *(roundkeys - 3) ^ last4bytes[13];
        roundkeys[14] = *(roundkeys - 2) ^ last4bytes[14];
        v4 = (char *)(last4bytes + 15);
        last4bytes += 16;
        v5 = *v4;
        v6 = *(roundkeys - 1);
        v7 = roundkeys + 15;
        roundkeys += 16;
        *v7 = v6 ^ v5;
      }
    }
    

看得出来是 TEA 加密后异或 delta 再 AES 加密，调试了下发现后面的 AES 与标准 AES 不太一样，也只好手动写逆了。

逆向程序：

    
    
    // clear && gcc -g ./main.c && ./a.out
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    typedef unsigned char uint8_t;
    unsigned char S[256] = { 99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22 };
    unsigned char INV_S[256] = {82, 9, 106, 213, 48, 54, 165, 56, 191, 64, 163, 158, 129, 243, 215, 251, 124, 227, 57, 130, 155, 47, 255, 135, 52, 142, 67, 68, 196, 222, 233, 203, 84, 123, 148, 50, 166, 194, 35, 61, 238, 76, 149, 11, 66, 250, 195, 78, 8, 46, 161, 102, 40, 217, 36, 178, 118, 91, 162, 73, 109, 139, 209, 37, 114, 248, 246, 100, 134, 104, 152, 22, 212, 164, 92, 204, 93, 101, 182, 146, 108, 112, 72, 80, 253, 237, 185, 218, 94, 21, 70, 87, 167, 141, 157, 132, 144, 216, 171, 0, 140, 188, 211, 10, 247, 228, 88, 5, 184, 179, 69, 6, 208, 44, 30, 143, 202, 63, 15, 2, 193, 175, 189, 3, 1, 19, 138, 107, 58, 145, 17, 65, 79, 103, 220, 234, 151, 242, 207, 206, 240, 180, 230, 115, 150, 172, 116, 34, 231, 173, 53, 133, 226, 249, 55, 232, 28, 117, 223, 110, 71, 241, 26, 113, 29, 41, 197, 137, 111, 183, 98, 14, 170, 24, 190, 27, 252, 86, 62, 75, 198, 210, 121, 32, 154, 219, 192, 254, 120, 205, 90, 244, 31, 221, 168, 51, 136, 7, 199, 49, 177, 18, 16, 89, 39, 128, 236, 95, 96, 81, 127, 169, 25, 181, 74, 13, 45, 229, 122, 159, 147, 201, 156, 239, 160, 224, 59, 77, 174, 42, 245, 176, 200, 235, 187, 60, 131, 83, 153, 97, 23, 43, 4, 126, 186, 119, 214, 38, 225, 105, 20, 99, 85, 33, 12, 125};
    unsigned char RC[10] = {1, 2, 4, 8, 16, 32, 64, 128, 27, 54};
    
    void shift_rows(uint8_t *state) {
        uint8_t temp; // [rsp+Fh] [rbp-1h]
        uint8_t tempa; // [rsp+Fh] [rbp-1h]
        uint8_t tempb; // [rsp+Fh] [rbp-1h]
        uint8_t tempc; // [rsp+Fh] [rbp-1h]
    
        temp = state[1];
        state[1] = state[5];
        state[5] = state[9];
        state[9] = state[13];
        state[13] = temp;
        tempa = state[2];
        state[2] = state[10];
        state[10] = tempa;
        tempb = state[6];
        state[6] = state[14];
        state[14] = tempb;
        tempc = state[15];
        state[15] = state[11];
        state[11] = state[7];
        state[7] = state[3];
        state[3] = tempc;
    }
    
    void inv_shift_rows(uint8_t *state) {
        uint8_t temp; // [rsp+Fh] [rbp-1h]
        uint8_t tempa; // [rsp+Fh] [rbp-1h]
        uint8_t tempb; // [rsp+Fh] [rbp-1h]
        uint8_t tempc; // [rsp+Fh] [rbp-1h]
    
        temp = state[13];
        state[13] = state[9];
        state[9] = state[5];
        state[5] = state[1];
        state[1] = temp;
        tempa = state[14];
        state[14] = state[6];
        state[6] = tempa;
        tempb = state[10];
        state[10] = state[2];
        state[2] = tempb;
        tempc = state[3];
        state[3] = state[7];
        state[7] = state[11];
        state[11] = state[15];
        state[15] = tempc;
    }
    
    uint8_t mul2(uint8_t a) {
        uint8_t result; // al
    
        if ( (a & 0x80u) == 0 )
            result = 2 * a;
        else
            result = (2 * a) ^ 0x1B;
        return result;
    }
    
    uint8_t muln(uint8_t a, uint8_t n) {
        uint8_t result = 0;
        while (n) {
            if (n & 1) result ^= a;
    
            if (a & 0x80) a = (a << 1) ^ 0x1B;
            else a <<= 1;
            n >>= 1;
        }
        return result;
    }
    
    void enc_next_ready(uint8_t *key, uint8_t *roundkeys) {
        uint8_t *v2; // rdx
        uint8_t *v3; // rax
        char *v4; // rax
        char v5; // r8
        char v6; // cl
        uint8_t *v7; // rax
        uint8_t temp_1; // [rsp+5h] [rbp-1Bh]
        uint8_t temp_2; // [rsp+6h] [rbp-1Ah]
        uint8_t temp_3; // [rsp+7h] [rbp-19h]
        uint8_t i; // [rsp+17h] [rbp-9h]
        uint8_t ia; // [rsp+17h] [rbp-9h]
        uint8_t *last4bytes; // [rsp+18h] [rbp-8h]
    
        for ( i = 0; i <= 15u; ++i ) {
            v2 = key++;
            v3 = roundkeys++;
            *v3 = *v2;
        }
        last4bytes = roundkeys - 4;
        for ( ia = 0; ia <= 9u; ++ia ) {
            temp_3 = S[*last4bytes];
            temp_1 = S[last4bytes[2]];
            temp_2 = S[last4bytes[3]];
            *roundkeys = *(roundkeys - 16) ^ S[last4bytes[1]] ^ RC[ia];
            roundkeys[1] = *(roundkeys - 15) ^ temp_1;
            roundkeys[2] = *(roundkeys - 14) ^ temp_2;
            roundkeys[3] = *(roundkeys - 13) ^ temp_3;
            roundkeys[4] = *(roundkeys - 12) ^ last4bytes[4];
            roundkeys[5] = *(roundkeys - 11) ^ last4bytes[5];
            roundkeys[6] = *(roundkeys - 10) ^ last4bytes[6];
            roundkeys[7] = *(roundkeys - 9) ^ last4bytes[7];
            roundkeys[8] = *(roundkeys - 8) ^ last4bytes[8];
            roundkeys[9] = *(roundkeys - 7) ^ last4bytes[9];
            roundkeys[10] = *(roundkeys - 6) ^ last4bytes[10];
            roundkeys[11] = *(roundkeys - 5) ^ last4bytes[11];
            roundkeys[12] = *(roundkeys - 4) ^ last4bytes[12];
            roundkeys[13] = *(roundkeys - 3) ^ last4bytes[13];
            roundkeys[14] = *(roundkeys - 2) ^ last4bytes[14];
            v4 = (char *)(last4bytes + 15);
            last4bytes += 16;
            v5 = *v4;
            v6 = *(roundkeys - 1);
            v7 = roundkeys + 15;
            roundkeys += 16;
            *v7 = v6 ^ v5;
        }
    }
    
    void dec_next_ready(uint8_t *key, uint8_t *roundkeys) {
        enc_next_ready(key, roundkeys);
    }
    
    void enc_next(uint8_t *roundkeys, uint8_t *plaintext, uint8_t *ciphertext) {
        double *v3; // rbx
        double *v4; // rax
        uint8_t *v5; // rax
        uint8_t *v6; // rax
        void *v7; // rax
        uint8_t *v8; // rax
        uint8_t tmp[16]; // [rsp+40h] [rbp-40h] BYREF
        char v11; // [rsp+5Eh] [rbp-22h] BYREF
        uint8_t t; // [rsp+5Fh] [rbp-21h]
        double temp_1; // [rsp+60h] [rbp-20h]
        int temp_0; // [rsp+6Ch] [rbp-14h]
        char temp; // [rsp+73h] [rbp-Dh]
        int a; // [rsp+74h] [rbp-Ch]
        int cnt; // [rsp+78h] [rbp-8h]
        uint8_t j; // [rsp+7Eh] [rbp-2h]
        uint8_t i; // [rsp+7Fh] [rbp-1h]
    
        for ( i = 0; i <= 15u; ++i ) {
            v6 = roundkeys++;
            ciphertext[i] = *v6 ^ plaintext[i] ^ 0x66;
        }
        for ( j = 1; j <= 9; j++ ) {
            for ( i = 0; i <= 15u; ++i )
                tmp[i] = INV_S[ciphertext[i]];
            inv_shift_rows(tmp);
            for ( i = 0; i <= 15; i += 4 ) {
                t = tmp[i + 2] ^ tmp[i + 1] ^ tmp[i] ^ tmp[i + 3];
                ciphertext[i] = t ^ tmp[i] ^ mul2(tmp[i] ^ tmp[i + 1]);
                ciphertext[i + 1] = t ^ tmp[i + 1] ^ mul2(tmp[i + 1] ^ tmp[i + 2]);
                ciphertext[i + 2] = t ^ tmp[i + 2] ^ mul2(tmp[i + 2] ^ tmp[i + 3]);
                ciphertext[i + 3] = t ^ tmp[i + 3] ^ mul2(tmp[i + 3] ^ tmp[i]);
            }
            for ( i = 0; i <= 15u; ++i ) {
                v8 = roundkeys++;
                ciphertext[i] ^= *v8;
            }
        }
    
        for ( i = 0; i <= 15u; ++i )
            ciphertext[i] = S[ciphertext[i]];
        shift_rows(ciphertext);
        for ( i = 0; i <= 0xFu; ++i ) {
            v5 = roundkeys++;
            ciphertext[i] ^= *v5;
        }
    }
    
    void dec_next(uint8_t *roundkeys, uint8_t *ciphertext, uint8_t *plaintext) {
        double *v3; // rbx
        double *v4; // rax
        uint8_t *v5; // rax
        uint8_t *v6; // rax
        void *v7; // rax
        uint8_t *v8; // rax
        uint8_t tmp[16]; // [rsp+40h] [rbp-40h] BYREF
        char v11; // [rsp+5Eh] [rbp-22h] BYREF
        uint8_t t; // [rsp+5Fh] [rbp-21h]
        double temp_1; // [rsp+60h] [rbp-20h]
        int temp_0; // [rsp+6Ch] [rbp-14h]
        char temp; // [rsp+73h] [rbp-Dh]
        int a; // [rsp+74h] [rbp-Ch]
        int cnt; // [rsp+78h] [rbp-8h]
        int j; // [rsp+7Eh] [rbp-2h]
        int i; // [rsp+7Fh] [rbp-1h]
    
        roundkeys += 176 - 1;
        for ( i = 15; i >= 0; i-- ) {
            v5 = roundkeys--;
            ciphertext[i] ^= *v5;
        }
        inv_shift_rows(ciphertext);
        for ( i = 15; i >= 0; i-- )
            ciphertext[i] = INV_S[ciphertext[i]];
    
        for ( j = 1; j <= 9; j++ ) {
            for ( i = 15; i >= 0; i-- ) {
                v8 = roundkeys--;
                ciphertext[i] ^= *v8;
            }
    
            for ( i = 0; i <= 15; i += 4 ) {
                tmp[i] = muln(ciphertext[i], 0xE) ^ muln(ciphertext[i + 1], 0xB) ^ muln(ciphertext[i + 2], 0xD) ^ muln(ciphertext[i + 3], 0x9);
                tmp[i + 1] = muln(ciphertext[i], 0x9) ^ muln(ciphertext[i + 1], 0xE) ^ muln(ciphertext[i + 2], 0xB) ^ muln(ciphertext[i + 3], 0xD);
                tmp[i + 2] = muln(ciphertext[i], 0xD) ^ muln(ciphertext[i + 1], 0x9) ^ muln(ciphertext[i + 2], 0xE) ^ muln(ciphertext[i + 3], 0xB);
                tmp[i + 3] = muln(ciphertext[i], 0xB) ^ muln(ciphertext[i + 1], 0xD) ^ muln(ciphertext[i + 2], 0x9) ^ muln(ciphertext[i + 3], 0xE);
            }
    
            shift_rows(tmp);
            for ( i = 15; i >= 0; i-- )
                ciphertext[i] = S[tmp[i]];
        }
    
        for ( i = 15; i >= 0; i-- ) {
            v6 = roundkeys--;
            plaintext[i] = *v6 ^ ciphertext[i] ^ 0x66;
        }
    }
    
    void aes_encrypt(char* data, char* key) {
        uint8_t roundkeys[256];
        char src[16];
        memcpy(src, data, 16);
        enc_next_ready(key, roundkeys);
        enc_next(roundkeys, src, data);
    }
    
    void aes_decrypt(char* data, char* key) {
        // todo: implement this method
        uint8_t roundkeys[256];
        char src[16];
        memcpy(src, data, 16);
        dec_next_ready(key, roundkeys);
        dec_next(roundkeys, src, data);
    }
    
    
    
    int main() {
        unsigned int delta = 0x73637466;
        // char data[33] = "0123456789abcdef";
        // cmp_arr
        char data[] = {
            0xBE, 0x1C, 0xB3, 0xF3, 0xA1, 0xF4, 0xE4, 0x63,
            0x11, 0xE1, 0x1C, 0x6B, 0x54, 0x0A, 0xDF, 0x74,
            0xF2, 0x93, 0x55, 0xDA, 0x48, 0xFC, 0xA2, 0x3C,
            0x89, 0x63, 0x2E, 0x7F, 0x8D, 0xA4, 0x6D, 0x4E,
            0
        };
    
        unsigned int* data_ptr = (unsigned int*) data;
        unsigned int v0, v1, v2, v3;
        char key[17] = "Welcome_to_sctf!";
        unsigned int* tea_key_ptr = (unsigned int*) key;
        unsigned int k0 = tea_key_ptr[0], k1 = tea_key_ptr[1], k2 = tea_key_ptr[2], k3 = tea_key_ptr[3];
        unsigned int sum1 = 0, sum2 = 0;
    
        /*
        char test_data[17] = "aaaaaaaaaaaaaaaa";
        aes_encrypt(test_data, key);
        for (int i = 0; i < 16; i++) {
            printf("0x%02x ", test_data[i] & 0xff);
        }
        // 0x33 0x18 0x46 0x7d 0x4a 0x1b 0x41 0xe5 0xc7 0x6e 0xf6 0x7a 0xd4 0x8a 0x6b 0x8c
        putchar('\n');
        /**/
    
    
        /*
        // tea
        for (int i = 0; i < 32; i++) {
            sum1 += delta;
            sum2 += delta;
            v0 += ((v1 << 4) + k2) ^ (v1 + sum1) ^ ((v1 >> 5) + k3) ^ (sum1 + i);
            v2 += ((v3 << 4) + k2) ^ (v3 + sum2) ^ ((v3 >> 5) + k3) ^ (sum2 + i);
    
            v1 += ((v0 << 4) + k0) ^ (v0 + sum1) ^ ((v0 >> 5) + k1) ^ (sum1 + i);
            v3 += ((v2 << 4) + k0) ^ (v2 + sum1) ^ ((v2 >> 5) + k1) ^ (sum2 + i);
        }
    
        data_ptr[0] = v0 ^ ((delta >> 24) & 0xff);
        data_ptr[1] = v1 ^ ((delta >> 16) & 0xff);
        data_ptr[2] = v2 ^ ((delta >> 8) & 0xff);
        data_ptr[3] = v3 ^ (delta & 0xff);
        /**/
    
        for (int loop = 0; loop < 2; loop++) {
            aes_decrypt((char*) data_ptr, key);
    
            data_ptr[3] ^= (delta & 0xff);
            data_ptr[2] ^= ((delta >> 8) & 0xff);
            data_ptr[1] ^= ((delta >> 16) & 0xff);
            data_ptr[0] ^= ((delta >> 24) & 0xff);
    
            v0 = data_ptr[0];
            v1 = data_ptr[1];
            v2 = data_ptr[2];
            v3 = data_ptr[3];
            for (int i = 0; i < 32; i++) {
                sum1 += delta;
                sum2 += delta;
            }
            for (int i = 31; i >= 0; i--) {
                v3 -= ((v2 << 4) + k0) ^ (v2 + sum1) ^ ((v2 >> 5) + k1) ^ (sum2 + i);
                v1 -= ((v0 << 4) + k0) ^ (v0 + sum1) ^ ((v0 >> 5) + k1) ^ (sum1 + i);
    
                v2 -= ((v3 << 4) + k2) ^ (v3 + sum2) ^ ((v3 >> 5) + k3) ^ (sum2 + i);
                v0 -= ((v1 << 4) + k2) ^ (v1 + sum1) ^ ((v1 >> 5) + k3) ^ (sum1 + i);
    
                sum2 -= delta;
                sum1 -= delta;
            }
            data_ptr[0] = v0;
            data_ptr[1] = v1;
            data_ptr[2] = v2;
            data_ptr[3] = v3;
            data_ptr += 4;
        }
        puts(data);
        /**/
    
        return 0;
    }
    

flag: SCTF{5277cc2af8f1155f7a61030f46fdf9df}

###  BabyDriver

babydriver.exe 拖入 ida ， initialize_pointers 中注册了异常处理函数 sub_140071500
，进入函数，有个参数，直接改类型为 PEXCEPTION_POINTERS ，逻辑一下就出来了：

    
    
    int __fastcall sub_140071500(PEXCEPTION_POINTERS e)
    {
      int result; // eax
    
      if ( e->ExceptionRecord->ExceptionCode == (unsigned int)EXCEPTION_ACCESS_VIOLATION )
      {
        e->ContextRecord->Rip = *(_QWORD *)e->ContextRecord->Rsp + 7i64;
        e->ContextRecord->Rsp += 8i64;
        result = EXCEPTION_CONTINUE_EXECUTION;
      }
      else if ( e->ExceptionRecord->ExceptionCode == (unsigned int)EXCEPTION_INT_DIVIDE_BY_ZERO )
      {
        funcs[e->ContextRecord->Rax]();
        e->ContextRecord->Rip += 8i64;
        result = EXCEPTION_CONTINUE_EXECUTION;
      }
      else
      {
        result = EXCEPTION_CONTINUE_SEARCH;
      }
      return result;
    }
    

这里先放着，待会要用的。

再回到 main ，直接一个 `MEMORY[0]()`，看汇编：

    
    
    .text:0000000140071318                 xor     eax, eax
    .text:000000014007131A                 call    rax
    .text:000000014007131C                 xor     eax, eax
    .text:000000014007131E                 jmp     loc_1400714DA
    

这 call 明显会触发 EXCEPTION_ACCESS_VIOLATION ，被上面的函数处理，`*(_QWORD
*)e->ContextRecord->Rsp`就是返回地址 0x14007131C ，再 + 7 就是 0x140071323 ，之后 rsp += 8
将返回地址弹出栈，所以什么都没做，直接将 call 指令 patch 为 jmp loc_14007131C:

    
    
    .text:0000000140071318                 xor     eax, eax
    .text:000000014007131A                 jmp     short loc_140071323 ; Keypatch modified this from:
    .text:000000014007131A                                         ;   call rax
    .text:000000014007131C ; ---------------------------------------------------------------------------    .text:000000014007131C                 xor     eax, eax
    .text:000000014007131E                 jmp     loc_1400714DA
    .text:0000000140071323 ; ---------------------------------------------------------------------------    

再 F5 ， main 就恢复了：

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      int result; // eax
      __int64 input_len; // [rsp+48h] [rbp-60h]
      HANDLE hFile; // [rsp+50h] [rbp-58h]
      DWORD NumberOfBytesRead; // [rsp+60h] [rbp-48h] BYREF
      char enc[16]; // [rsp+68h] [rbp-40h] BYREF
      char input[21]; // [rsp+78h] [rbp-30h] BYREF
    
      input[0] = 0;
      memset(&input[1], 0, 20ui64);
      enc[0] = 0;
      memset(&enc[1], 0, 15ui64);
      initialize_pointers();
      if ( query(0, 0i64, 0) )
      {
        hFile = CreateFileA("key.bin", GENERIC_READ, FILE_SHARE_READ, 0i64, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0i64);
        if ( hFile == (HANDLE)-1i64 )
        {
          printf("Can't not find the key file\n");
          result = 0;
        }
        else
        {
          NumberOfBytesRead = 0;
          if ( ReadFile(hFile, Buffer, 0x258u, &NumberOfBytesRead, 0i64) )
          {
            printf("Please input the flag:");
            scanf("%s", input);
            input_len = -1i64;
            do
              ++input_len;
            while ( input[input_len] );
            if ( test_charset(input, input_len)
              && run_function(input, input_len, enc)
              && (query(2, (__int64)enc, 16u), Sleep(500u), query(1, (__int64)enc, 16u), enc[0]) )
            {
              printf("Success!!!\n");
              result = 0;
            }
            else
            {
              printf("You fail.\n");
              result = 0;
            }
          }
          else
          {
            printf("Can't not read the key file\n");
            result = 0;
          }
        }
      }
      else
      {
        printf("Driver not running");
        result = 0;
      }
      return result;
    }
    

query 函数很奇怪：

    
    
    _BOOL8 __fastcall query(int a1, __int64 a2, unsigned int a3)
    {
      struct _SYSTEMTIME SystemTime; // [rsp+28h] [rbp-40h] BYREF
      __int64 v5[3]; // [rsp+38h] [rbp-30h] BYREF
      __int64 v6; // [rsp+50h] [rbp-18h]
    
      v5[0] = a1;
      v5[1] = a2;
      v5[2] = a3;
      v6 = 1i64;
      memset(&SystemTime, 0, sizeof(SystemTime));
      GetSystemTime(&SystemTime);
      *(_QWORD *)qword_14009DED8 = v5;
      SetSystemTime(&SystemTime);
      return v6 == 0;
    }
    

按理说 return v6 == 0 只会返回 0 ，那么 main 中就会输出 “Driver not running” 并结束，想到题目名叫
BabyDriver ，那就还得分析另一个文件 sctf.sys 。同样拖入 ida ，进入 DriverEntry ，跟入 sub_140001078 ：

    
    
    __int64 __fastcall sub_140001078(PDRIVER_OBJECT a1)
    {
      sub_1400010CC(sub_140001000);
      a1->DriverUnload = (PDRIVER_UNLOAD)sub_1400010A0;
      return 0i64;
    }
    

跟入 sub_1400010CC ：

    
    
    __int64 __fastcall sub_1400010CC(__int64 (__fastcall *a1)(__int64))
    {
      UNICODE_STRING v3; // [rsp+20h] [rbp-40h] BYREF
      struct _OBJECT_ATTRIBUTES ObjectAttributes; // [rsp+30h] [rbp-30h] BYREF
      PCALLBACK_OBJECT CallbackObject; // [rsp+78h] [rbp+18h] BYREF
    
      CallbackObject = 0i64;
      v3.Buffer = L"\\Callback\\SetSystemTime";
      *(_DWORD *)&v3.Length = 0x30002E;
      memset(&ObjectAttributes, 0, sizeof(ObjectAttributes));
      ObjectAttributes.Length = 48;
      ObjectAttributes.ObjectName = &v3;
      ObjectAttributes.Attributes = 80;
      if ( ExCreateCallback(&CallbackObject, &ObjectAttributes, 1u, 1u) < 0 )
        return 0xC0000225i64;
      CallbackRegistration = ExRegisterCallback(CallbackObject, (PCALLBACK_FUNCTION)CallbackFunction, 0i64);
      if ( !CallbackRegistration )
        return 0xC0000225i64;
      func_140001000 = a1;
      return 0i64;
    }
    

原来 Driver 注册了 SetSystemTime 函数的回调函数 CallbackFunction ：

    
    
    KIRQL __fastcall sub_14000123C(__int64 a1)
    {
      _BYTE *v1; // rcx
      KIRQL result; // al
    
      if ( *(_DWORD *)a1 == 2 )
      {
        v1 = *(_BYTE **)(a1 + 8);
        v1[15] = v1[14];
        v1[14] = v1[13];
        v1[13] = v1[12];
        v1[12] = 0x10;
        result = KeGetCurrentIrql();
      }
      return result;
    }
    
    void __fastcall CallbackFunction(PVOID CallbackContext, PVOID Argument1, PVOID Argument2)
    {
      struct _KPROCESS *v3; // rdi
      void *v4; // rax
      void *v5; // rbx
      PEB *v6; // rax
      KIRQL v7; // al
      unsigned __int64 v8; // rdi
      _BYTE *v9; // rcx
    
      v3 = IoGetCurrentProcess();
      v4 = (void *)PsGetProcessWow64Process(v3);
      v5 = 0i64;
      if ( v4 )
      {
        v5 = (void *)*((unsigned int *)v4 + 5);
        *((_DWORD *)v4 + 5) = 0;
      }
      else
      {
        v6 = PsGetProcessPeb(v3);
        if ( v6 )
        {
          v5 = v6->SubSystemData;
          v6->SubSystemData = 0i64;
        }
      }
      if ( MmIsAddressValid(v5) )
      {
        v7 = sub_14000123C((__int64)v5);
        v8 = v7;
        if ( v7 >= 2u )
          __writecr8(0i64);
        *((_QWORD *)v5 + 3) = (int)func_140001000(v5);
        if ( (unsigned __int8)v8 >= 2u )
        {
          KeGetCurrentIrql();
          __writecr8(v8);
        }
        if ( *(_DWORD *)v5 == 2 )
        {
          v9 = (_BYTE *)*((_QWORD *)v5 + 1);
          v9[12] = v9[13];
          v9[13] = v9[14];
          v9[14] = v9[15];
          v9[15] = 0;
        }
      }
    }
    

这里调用了 sub_1400010CC 传入的参数函数 sub_140001000，并将返回值赋值给 `*((_QWORD *)v5 + 3)`。

    
    
    __int64 __fastcall sub_140001000(void *a1)
    {
      int v1; // er8
      unsigned int *v2; // r9
      __int64 i; // rcx
    
      v1 = 0;
      if ( *(_DWORD *)a1 )
      {
        if ( *(_DWORD *)a1 == 1 )
        {
          **((_BYTE **)a1 + 1) = byte_140003070;
        }
        else if ( *(_DWORD *)a1 == 2 )
        {
          v2 = (unsigned int *)*((_QWORD *)a1 + 1);
          for ( i = 0i64; i < 32; i += 8i64 )
          {
            if ( *(_QWORD *)(i + 0x140003008i64) * (unsigned __int64)*v2 % 0x30F21223F13Bi64 != *(_QWORD *)(i + 0x140003028i64) )
              break;
            ++v1;
            ++v2;
          }
          byte_140003070 = v1 == 4;
        }
      }
      else
      {
        byte_140003070 = 0;
      }
      return 0i64;
    }
    

这里的返回值为 0 ，联想到 main 中的 query 函数，返回 v6 == 0 就为 1 了，所以 CallbackFunction 中的 v5 就是
query 函数中的 v5 ， v5[3] 就刚好是 v6 。

明白了这两者的关系，就先分析 sub_140001000 吧，这个文件里只有这一个函数比较可疑了。

`*(_DWORD *)a1`存放的值表明函数需要做什么，如果为 0 ，执行`byte_140003070 = 0;`，如果为 1
，执行`**((_BYTE **)a1 + 1) = byte_140003070;`，如果为 2 ，执行中间的四轮判断，是`a[i] * x[i] % p
== b[i]`这样的形式， a, b, p 是固定值， x 是传入的`(unsigned int *)*((_QWORD *)a1 + 1)`，就能猜到
main 中将输入操作后得到 4 个 int ，再在这里执行判断。这样就先计算出这 4 个 int 。先在 0x140003008 找到这 8 个数：

    
    
    .data:0000000140003000 ; const __int64 qword_140003000
    .data:0000000140003000 qword_140003000 dq 53816244564283       ; DATA XREF: sub_140001000+2F↑r
    .data:0000000140003008                 dq 649430213, 895805425, 751586893, 3859015203
    .data:0000000140003028                 dq 49033969837712, 36224070408864, 1911652611622, 32147829792607
    

编写简单脚本反解：

    
    
    #!/usr/bin/python2
    
    from gmpy2 import invert
    
    # a[i] * x[i] % p = b[i]
    p = 53816244564283
    a = [649430213, 895805425, 751586893, 3859015203]
    b = [49033969837712, 36224070408864, 1911652611622, 32147829792607]
    
    x = [0] * 4
    
    for i in range(4):
        x[i] = int(invert(a[i], p)) * b[i] % p
        # assert(x[i] * a[i] % p == b[i])
        print(hex(x[i]))
    
    '''
    0xd4933333
    0x7bde8f00
    0x31d84f77
    0xbcd47c10 -> 0xbcd47c
    '''
    

并且注意到 x[3] & 0xff == 0x10，而在 sub_14000123C 中多加了一个 0x10 ，所以实际上的输入 x[3] 只有 24
位，最后的 0x10 是回调函数里补的。也就是说，转成 uchar ， x 只有 15 字节。

再回到 main ， query(0) 后读取文件 key.bin ，但是并没有给这个文件。

之后输入 flag ， test_charset 函数判断输入的字符是否在
‘0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{|}’
中，并将该字符换成字符在此串中的下标。

紧接着来到 run_function ，又是`MEMORY[0]()`，不多说，改成 jmp ，再 F5 ：

    
    
    _BOOL8 __fastcall run_function(char *input, unsigned int a2, char *enc)
    {
      int i; // [rsp+20h] [rbp-28h]
      int j; // [rsp+24h] [rbp-24h]
      int v6; // [rsp+28h] [rbp-20h]
    
      for ( i = 0; i < 600; ++i )
      {
        v6 = (unsigned __int8)Buffer[i];
        for ( j = 0; j < 8; ++j )
        {
          if ( (v6 & 1) != 0 )
          {
            _input = input;
            _enc = enc;
          }
          v6 >>= 1;
        }
      }
      return point == 0;
    }
    

看起来很奇怪，什么都没做？这里需要看一下汇编：

    
    
    .text:000000014007186A                 mov     eax, [rsp+48h+j]
    .text:000000014007186E                 mov     ecx, [rsp+48h+i]
    .text:0000000140071872                 lea     eax, [rax+rcx*8]
    .text:0000000140071875                 cdqe
    .text:0000000140071877                 xor     edx, edx
    .text:0000000140071879                 xor     ecx, ecx
    .text:000000014007187B                 div     rcx
    .text:000000014007187E                 mov     [rsp+48h+var_18], rax
    .text:0000000140071883
    .text:0000000140071883 loc_140071883:                          ; CODE XREF: run_function+75↑j
    .text:0000000140071883                 mov     eax, [rsp+48h+var_20]
    

有一个除零异常，被 ida 忽略掉了，但是这是关键，要用到注册的异常处理函数第二个 if EXCEPTION_INT_DIVIDE_BY_ZERO
，调用函数`funcs[e->ContextRecord->Rax]()`，读汇编计算 rax = i * 8 + j ，所以真实的逻辑应该是：

    
    
    _BOOL8 __fastcall run_function(char *input, unsigned int a2, char *enc)
    {
      int i; // [rsp+20h] [rbp-28h]
      int j; // [rsp+24h] [rbp-24h]
      int v6; // [rsp+28h] [rbp-20h]
    
      for ( i = 0; i < 600; ++i )
      {
        v6 = (unsigned __int8)Buffer[i];
        for ( j = 0; j < 8; ++j )
        {
          if ( (v6 & 1) != 0 )
          {
            _input = input;
            _enc = enc;
            funcs[i * 8 + j]();
          }
          v6 >>= 1;
        }
      }
      return point == 0;
    }
    

.data 段中查看 funcs ，是个大小为 3600 的函数数组，这不可能一个一个去分析。随便找几个查看，函数都是这样的形式：

    
    
    _enc[e] |= ((_input[a] >> b) & c) << d;
    point -= f;
    

其中`_enc`和`_input`是全局变量，由上面函数的参数赋值；`point`也是全局变量，初始值为 3100 ； a~f 都是代码中的常值。

这样就写个脚本提取出 a~f 这几个参数，处理过程中发现 a 的取值为 [0, 19] ， b 的取值为 {0, 2, 4} ， c 是固定的 3 ， d
的取值为 {0, 2, 4, 6} ， e 的取值为 [0, 14] ，这样计算一下不重复的组合刚好是 20 _3_ 4 _15 == 3600 ，也就是
funcs 数组的大小；由于 c 是固定的 3 ，也就是每个函数将`_input`中的 2bit 复制到`_enc`的 2bit
上，而`_enc`和`_input`的 2bit 数又是相等的： 20 _ 3 == 60 == 4 * 15 ，这样自然就抽象出一个算法问题：

    
    
    两个集合 A、B 均有 60 个元素
    A 中任一元素到 B 中任一元素均有一给定的映射权值
    求 A 到 B 的一一映射，使得映射权值和为给定值（3100）
    

问了下打算法的同学，这个求解不太乐观，还是得自己想办法。

看了下权值，大部分的都是3位数，而权值平均数 3100 / 60 < 60
，可能是求一个最小值，这样就有思路了，先提取出权值矩阵，找出每行的最小值及下标，然后观察发现权值和为 3044 ，并且只有一个重复的下标值 20
，缺少的下标值为 21 ，再将相关的值输出出来：

    
    
    >>> values[13][20]
    101
    >>> values[50][20]
    64
    >>> values[13][21]
    157
    >>> values[50][21]
    151
    

`values[13][21]` 与 `values[13][20]` 刚好相差 56 ，也就是 3100 – 3044 ，所以将 13 映射到 21
，这样就找到了解，再反过来求解 flag 。

    
    
    #!/usr/bin/python2
    
    from gmpy2 import invert
    
    # a[i] * x[i] % p = b[i]
    p = 53816244564283
    a = [649430213, 895805425, 751586893, 3859015203]
    b = [49033969837712, 36224070408864, 1911652611622, 32147829792607]
    
    x = [0] * 4
    
    for i in range(4):
        x[i] = int(invert(a[i], p)) * b[i] % p
        # assert(x[i] * a[i] % p == b[i])
        # print(hex(x[i]))
    
    '''
    0xd4933333
    0x7bde8f00
    0x31d84f77
    0xbcd47c10 -> 0xbcd47c
    '''
    assert((x[3] & 0xff) == 0x10)
    x[3] >>= 8
    # convert x to byte array
    y = []
    for i in x:
        y.append(i & 0xff)
        y.append((i >> 8) & 0xff)
        y.append((i >> 16) & 0xff)
        y.append((i >> 24) & 0xff)
    
    assert(y[-1] == 0)
    x = y[: -1]
    del y
    
    def qword(data, index):
        x = 0
        for i in range(8):
            x |= ord(data[i + index]) << (i * 8)
        return x
    
    def dword(data, index):
        x = 0
        for i in range(4):
            x |= ord(data[i + index]) << (i * 8)
        return x
    
    with open('./babydriver.exe', 'rb') as f:
        data = f.read()
    
    def parse_func_fail(i, j):
        print 'fail:', i, j
        exit(-1)
    
    funcs = []
    size = 3600
    for i in range(size):
        addr = qword(data, 8 * i + 0x93630) - 0x140000C00
        s = ''
        while True:
            s += data[addr]
            if s[-4: -1] == '\xCC\xCC\xCC': break
            addr += 1
        if s[4: 9] != '\xB8\x01\x00\x00\x00': # mov eax, 1
            parse_func_fail(i, 0)
        if s[9: 12] != '\x48\x6B\xC0': # imul rax, 0x??
            parse_func_fail(i, 1)
        a = ord(s[12])
        s = s[13: ]
        if s[11: 13] == '\xC1\xF8': # sar eax, 0x??
            b = ord(s[13])
            s = s[14: ]
        elif s[11: 14] == '\x88\x04\x24':
            b = 0
            s = s[11:]
        else:
            parse_func_fail(i, 2)
    
        if s[7: 9] != '\x83\xE0': # and eax, 0x??
            parse_func_fail(i, 3)
        c = ord(s[9])
        s = s[10: ]
        if s[7: 9] == '\xC1\xE0': # shl eax, 0x??
            d = ord(s[9])
            s = s[10: ]
        elif s[7: 10] == '\x88\x04\x24':
            d = 0
            s = s[7: ]
        else:
            parse_func_fail(i, 4)
        if s[8: 11] != '\x48\x6B\xC0': # imul rax, 0x??
            parse_func_fail(i, 5)
        e = ord(s[11])
        s = s[12: ]
        if s[15: 17] != '\x0B\xC1': # or eax, ecx
            parse_func_fail(i, 6)
        s = s[17: ]
        if s[26: 28] == '\x48\x2D': # sub rax, 0x????????
            f = dword(s, 28)
            s = s[32: ]
        elif s[26: 29] == '\x48\x83\xE8': # sub rax, 0x??
            f = ord(s[29])
            s = s[30: ]
        elif s[26: 29] == '\x48\xFF\xC8': # dec rax
            f = 1
            s = s[29: ]
        else:
            parse_func_fail(i, 7)
    
        if s[11] != '\xC3':
            parse_func_fail(i, 8)
    
        '''
        enc[e] |= ((input[a] >> b) & c) << d;
        point -= f
        '''
        assert(c == 3)
        # funcs.append([a, b, c, d, e, f])
    
        # change order to sort
        funcs.append([e, d, a, b, f, i])
    
    funcs.sort()
    point_total = 3100
    
    # 3 * 20 == 60 == 4 * 15
    # 3 * 20 * 4 * 15 == 3600
    # for i in range(size): print i, funcs[i]
    
    values = []
    for i in range(60):
        values.append([])
        for j in range(60):
            values[-1].append(funcs[60 * i + j][4])
    
    
    '''
    with open('./values', 'w') as f:
        f.write(str(values))
    '''
    
    result = [i for i in range(60)]
    '''
    calculate result
    '''
    result = [59, 43, 45, 46, 7, 27, 9, 11, 26, 42, 31, 25, 0, 21, 24, 34, 54, 55, 22, 39, 40, 44, 5, 41, 28, 1, 38, 48, 58, 29, 16, 51, 49, 15, 33, 8, 4, 50, 53, 6, 23, 12, 19, 13, 30, 17, 37, 3, 47, 32, 20, 36, 52, 18, 2, 14, 56, 35, 10, 57]
    
    flag = [0] * 20
    for i in range(60):
        flag[result[i] / 3] |= ((x[i / 4] >> (i % 4 * 2)) & 3) << (result[i] % 3 * 2)
    
    table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{|}'
    for i in range(len(flag)):
        flag[i] = table[flag[i]]
    
    print(''.join(flag))
    

最后一个 ‘{‘ 转成 ‘}’ 即可。

flag: SCTF{Dr1ver|Tim3|10}

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Ichild** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264281](/post/id/264281)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __6赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/LMicarFC5m2cLIeu7Rlg2TgkcvFQrOCchdA1ia1ZlunvFv4Mk1uJHJLibGDJTRZnDBm1nS2cicvKzRVp0AsSib0lUqA/132)
Ichild

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

