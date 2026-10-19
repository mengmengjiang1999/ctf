开发调试器，必然就会涉及反汇编，反汇编引擎的功能和性能的指标也是其中最主要的部分，势必就会涉及到对反汇编引擎的对比于选择。

本文选择的是udis86，od的反汇编引擎[
**ODDisassm**](http://www.ollydbg.de/)虽然简洁，但是只支持x86intel的汇编指令，不支持x64，指令集也很陈旧，
**BeaEngine** 虽然也不错支持新指令集也多，但是代码风格看起来不爽， **capstone**
虽然支持指令集比较多，也支持移动arm指令，但是整体代码比较复杂，庞大臃肿，改造成本太高，最后还是选择了 **udis86**
，代码和接口都非常简洁只有几个cpp/h文件，支持支持MMX, FPU (x87), AMD 3DNow, SSE, SSE2, SSE3, SSSE3,
SSE4.1, SSE4.2, AES, AMD-V, INTEL-VMX,
SMX，支持x86/x64的Intel/AT&A的指令平台，还有一个最大的特点就是解码速度非常快。

 **1.** **udis86** **的使用**

udis86的接口很简单，使用也很简单

**一、第一步是初始化**

ud_t ud_obj;

ud_init(&ud_obj);

ud_set_mode(&ud_obj,16); 设置反汇编系统16/32/64位

ud_set_pc(u, 0); 设置内存的段的基址，相当于PE文件的基址。

ud_set_asm_buffer(u,u->asm_buf_int,sizeof(u->asm_buf_int)); 设置反汇编的数据原始地址和数据长度

ud_set_syntax(&ud_obj, UD_SYN_INTEL);设置反汇编的语法平台

**二、第二步反汇编调用**

代码示例：

while (ud_disassemble(&ud_obj)) {

if (o_do_off)

_printf_ ("%016"FMT64 "x", ud_insn_off(&ud_obj));

if (o_do_hex) {

const char* hex1, *hex2;

hex1 = ud_insn_hex(&ud_obj);

hex2 = hex1 \+ 16;

_printf_ ("%-16.16s%-24s", hex1, ud_insn_asm(&ud_obj));

if ( _strlen_ (hex1) > 16) {

//printf("\n");

if (o_do_off)

_printf_ ("%15s-", "");

_printf_ ("%-16s",hex2);

}

}

else _printf_ (" %-24s", ud_insn_asm(&ud_obj));

_printf_ ("\n");

}

ud_disassemble(&ud_obj)反汇编解析指令

ud_disassemble里调用ud_decode函数来实现解码分析操作，然后使用translator函数对解码的结果做指令翻译操作翻译成可读的
intel或者AT&T的语法字符串。

ud_insn_off(&ud_obj)获得当前的指令地址

ud_insn_asm(&ud_obj)获取当前的反汇编后的字符串。

一下是结果显示：

![TIM图片20180305230429.png](https://image.3001.net/images/20180305/1520262310485.png!small)

**三、符号的设置**  

udis86还提供了一个设置解析符号的函数接口

ud_set_sym_resolver(&ud_obj,resolver);

resolver的接口定义：

const char* (*resolver)(struct ud*,

_uint64_t_ _addr_ ,

_int64_t_ *offset)

我们可以看到代码里

void

ud_syn_print_addr(struct ud *u, _uint64_t_ addr,char
operand_asm_buf[64],int*index)

{

const char *name = _NULL_ ;

if (u->sym_resolver) {

_int64_t_ offset =0;

name = u->sym_resolver(u, addr, &offset);

if (name) {

if (offset) {

ud_asmprintf(u, "%s%+" FMT64"d", name,offset);

ud_asmprintf2(operand_asm_buf,index,"%s%+"FMT64 "d",name, offset);

} else {

ud_asmprintf(u, "%s", name);

ud_asmprintf2(operand_asm_buf,index, "%s",name);

}

return;

}

}

ud_asmprintf(u, "%" FMT64"X", addr);

ud_asmprintf2(operand_asm_buf,index, "%"FMT64 "X",addr);

}

如果设置了sym_resolver接口，就会调用这个接口反汇的符号字符串来替代地址值的反汇编字符串。

纵观以上udis86提供不少的功能但是在冒些情况下有很多不足之处，比如在一块很大的内存进行反汇编解码时没有预解码的函数接口，会导致使用者误认为效率不高，还有其他情况与我们使用ollydbg不同的语法风格也需要我们去改造。

**2\. udis86改造**

**一、增加预分析接口。**

unsigned int ud_predecode(struct ud* u)

{

int len;

if (u->inp_end) {

return 0;

}

len = ud_decode(u);

return len;

}

这个函数在分析解析过程速度非常快，效率非常高，这个函数用处主要在预分析，确定当前内存数据能反汇编出多少行指令，方便后续界面显示时分页显示，因为它少了translator过程，预分析过程效率提高了几百上千倍。

**二．** **地址前缀显示的改造**

udis86在地址取址的前缀结果显示与ollydbg不同，例如

static void

opr_cast(struct ud* u, struct ud_operand* op)

{

if (u->br_far) {

ud_asmprintf(u, "far ");

}

switch(op->size) {

case 8: ud_asmprintf(u, "byte " ); break;

case 16: ud_asmprintf(u, "word "); break;

case 32: ud_asmprintf(u, "dword ");break;

case 64: ud_asmprintf(u, "qword ");break;

case 80: ud_asmprintf(u, "tword ");break;

default: break;

}

}

为了保持了ollydbg一直我们需要改成:

switch(op->size) {

case 8: ud_asmprintf(u, "BYTE PTR ");ud_asmprintf2(operand_asm_buf,index,"BYTE
PTR"); break;

case 16: ud_asmprintf(u, "WORD PTR "
);ud_asmprintf2(operand_asm_buf,index,"WORD PTR "); break;

case 32: ud_asmprintf(u, "DWORD PTR
");ud_asmprintf2(operand_asm_buf,index,"DWORD PTR "); break;

case 64: ud_asmprintf(u, "QWORD PTR
");ud_asmprintf2(operand_asm_buf,index,"QWORD PTR "); break;

case 80: ud_asmprintf(u, "TWORD PTR
");ud_asmprintf2(operand_asm_buf,index,"TWORD PTR "); break;

default: break;

}

 **三、** **X64 RIP call** **指令不能显示符号地址** ****

 ****

 ****

这个应该属于 bug显示问题，所以我们需要做以下修改，问题主要在ud_syn_print_mem_disp

函数，原是函数代码为：

void

ud_syn_print_mem_disp(struct ud* u, const struct ud_operand *op, int sign,char
operand_asm_buf[64], int*index)

{

UD_ASSERT(op->offset != 0);

if (op->base == UD_NONE&& op->index== UD_NONE) {

_uint64_t_ v;

UD_ASSERT(op->scale == UD_NONE&& op->offset!= 8);

/* unsigned mem-offset */

switch (op->offset) {

case 16: v = op->lval.uword; break;

case 32: v = op->lval.udword; break;

case 64: v = op->lval.uqword; break;

default: UD_ASSERT(!"invalid offset"); v = 0; /* keep cc happy */

}

ud_asmprintf(u, "%" FMT64"X", v);

ud_asmprintf2(operand_asm_buf,index, "%"FMT64 "X",v);

} else {

_int64_t_ v;

UD_ASSERT(op->offset != 64);

switch (op->offset) {

case 8 : v = op->lval.sbyte; break;

case 16: v = op->lval.sword; break;

case 32: v = op->lval.sdword; break;

default: UD_ASSERT(!"invalid offset"); v = 0; /* keep cc happy */

}

if (v < 0) {

ud_asmprintf(u, "-%" FMT64"X", -v);

ud_asmprintf2(operand_asm_buf,index,"-%" FMT64"X", -v);

} else if (v > 0) {

ud_asmprintf(u, "%s%" FMT64"X", sign?"+" : "",v);

ud_asmprintf2(operand_asm_buf,index,"%s%" FMT64"X", sign?"+" : "",v);

}

}

}

修复主要在后面加一个RIP指令判断

void ud_syn_print_mem_disp(

struct ud* u,

struct ud_operand *op,

int sign)

{

UD_ASSERT(op->offset != 0);

if (op->base == UD_NONE&& op->index== UD_NONE)

{

_uint64_t_ v;

UD_ASSERT(op->scale == UD_NONE&& op->offset!= 8);

/* unsigned mem-offset */

switch (op->offset)

{

case 16: v = op->lval.uword; break;

case 32: v = op->lval.udword; break;

case 64: v = op->lval.uqword; break;

default: UD_ASSERT(!"invalid offset"); v = 0; /* keep cc happy */

}

if (u->sym_resolver)

{

_LPTSTR_ name = _NULL_ ;

_int64_t_ offset =0;

name = u->sym_resolver(u, v, &offset);

if (name)

{

if (offset)

{

op->_legacy = offset;

ud_asmprintf(u,0, __T_ ("%s.%")FMT64 __T_ ("X"), name,offset);

}

else

{

op->_legacy = v;

ud_asmprintf(u,0, __T_ ("%s"),name);

}

return;

}

}

ud_asmprintf(u,1, __T_ ("%")FMT64 __T_ ("X"), v);

}

else

{

_int64_t_ v;

UD_ASSERT(op->offset != 64);

switch (op->offset)

{

case 8 : v = op->lval.sbyte; break;

case 16: v = op->lval.sword; break;

case 32: v = op->lval.sdword; break;

default: UD_ASSERT(!"invalidoffset"); v = 0; /* keep cc happy */

}

//这里为添加专门处理RIP的指令

if (op->base == UD_R_RIP)

{

v += (u->inp_ctr \+ u->insn_offset);

if (u->sym_resolver)

{

_LPTSTR_ name = _NULL_ ;

_int64_t_ offset = 0;

name = u->sym_resolver(u, v, &offset);

if (name)

{

if (offset)

{

op->_legacy = offset;

ud_asmprintf(u,0, __T_ ("%s.%") FMT64 __T_ ("X"),name, offset);

}

else

{

op->_legacy = v;

ud_asmprintf(u,0, __T_ ("%s"), name);

}

return;

}

}

}

if (v < 0)

{

ud_asmprintf(u,1, __T_ ("-%") FMT64 __T_ ("X"),-v);

}

else if (v > 0)

{

if (op->base == UD_R_RIP)

{

ud_asmprintf(u,1, __T_ ("%s%") FMT64 __T_ ("X"),sign? __T_ ("") : __T_ (""),
v);

}else

{

ud_asmprintf(u,1, __T_ ("%s%") FMT64 __T_ ("X"),sign? __T_ ("+") : __T_ (""),
v);

}

}

}

}

其他还有一些小的细节和ollydbg有细微差别，这里就不再赘述了，读者可以自行去发现，经过一些改造与加工我们就能得到一个性能与结果完美的反汇编引擎，后面的一些界面显示的速度性能等等一些调试器的交互工作就会事半功倍了。  
  

