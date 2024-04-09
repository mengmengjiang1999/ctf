int _init(unsigned int a0, unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5, unsigned long long v1, unsigned long long a6, unsigned long long a7, unsigned long long a8, unsigned long long a9, unsigned long a10)
{
    char v0;  // [bp+0x0]

    if (true)
        return;
    0(a0, a1, a2, a3, a4, a5, *((long long *)&v0), v1, a6, a7, a8, a9);
    return;
}

long long sub_400630()
{
    void* v0;  // [bp-0x8]

    v0 = 0;
    goto *((long long *)6295464);
}

extern unsigned long long __libc_csu_fini;
extern unsigned long long __libc_csu_init;
extern unsigned long long main;

long long _start()
{
    unsigned long v0;  // [bp+0x0], Other Possible Types: char
    unsigned long v1;  // [bp+0x8]
    unsigned long long v2;  // rsi
    unsigned long v3;  // rax
    unsigned long long v4;  // rdx

    v2 = *((long long *)&v0);
    v0 = v3;
    __libc_start_main(&main, v2, &v1, &__libc_csu_init, &__libc_csu_fini, v4); /* do not return */
}

// No decompilation output for function sub_4006ca

extern char __TMC_END__;

int deregister_tm_clones()
{
    if (true)
        return;
    if (!(false))
        return;
}

long long register_tm_clones()
{
    if (true)
        return 0;
    if (true)
        return 0;
}

extern char __TMC_END__;

long long __do_global_dtors_aux()
{
    unsigned long v0;  // [bp-0x8]
    char v1;  // [bp+0x0]
    unsigned long v3;  // rax

    if (__TMC_END__)
        return v3;
    v0 = &v1;
    if (true)
    {
        __TMC_END__ = 1;
        return deregister_tm_clones();
    }
    __cxa_finalize();
    __TMC_END__ = 1;
    return deregister_tm_clones();
}

long long frame_dummy()
{
    return register_tm_clones();
}

int xor_transform(char *a0, unsigned int a1)
{
    unsigned int v0;  // [bp-0xc]

    for (v0 = 0; a0[v0]; v0 += 1)
    {
        a0[v0] = a0[v0] ^ (char)a1;
    }
    return;
}

int main()
{
    char v0;  // [bp-0xc8]
    char v1;  // [bp-0xc7]
    char v2;  // [bp-0xc6]
    char v3;  // [bp-0xc5]
    char v4;  // [bp-0xc4]
    char v5;  // [bp-0xc3]
    char v6;  // [bp-0xc2]
    char v7;  // [bp-0xc1]
    char v8;  // [bp-0xc0]
    char v9;  // [bp-0xbf]
    char v10;  // [bp-0xbe]
    char v11;  // [bp-0xbd]
    char v12;  // [bp-0xbc]
    char v13;  // [bp-0xbb]
    char v14;  // [bp-0xba]
    char v15;  // [bp-0xb9]
    char v16;  // [bp-0xb8]
    char v17;  // [bp-0xb7]
    char v18;  // [bp-0xb6]
    char v19;  // [bp-0xb5]
    char v20;  // [bp-0xb4]
    char v21;  // [bp-0xb3]
    char v22;  // [bp-0xb2]
    char v23;  // [bp-0xb1]
    char v24;  // [bp-0xb0]
    char v25;  // [bp-0xaf]
    char v26;  // [bp-0xae]
    char v27;  // [bp-0xad]
    char v28;  // [bp-0xac]
    char v29;  // [bp-0xab]
    char v30;  // [bp-0xaa]
    char v31;  // [bp-0xa9]
    char v32;  // [bp-0xa8]
    char v33;  // [bp-0xa7]
    char v34;  // [bp-0xa6]
    char v35;  // [bp-0xa5]
    char v36;  // [bp-0xa4]
    char v37;  // [bp-0xa3]
    char v38;  // [bp-0xa2]
    char v39;  // [bp-0xa1]
    char v40;  // [bp-0xa0]
    char v41;  // [bp-0x9f]
    char v42;  // [bp-0x9e]
    char v43;  // [bp-0x9d]
    char v44;  // [bp-0x9c]
    char v45;  // [bp-0x9b]
    char v46;  // [bp-0x9a]
    char v47;  // [bp-0x99]
    char v48;  // [bp-0x98]
    char v49;  // [bp-0x97]
    char v50;  // [bp-0x96]
    char v51;  // [bp-0x95]
    char v52;  // [bp-0x94]
    char v53;  // [bp-0x93]
    char v54;  // [bp-0x92]
    char v55;  // [bp-0x91]
    char v56;  // [bp-0x90]
    char v57;  // [bp-0x8f]
    char v58;  // [bp-0x8e]
    char v59;  // [bp-0x8d]
    char v60;  // [bp-0x8c]
    char v61;  // [bp-0x8b]
    char v62;  // [bp-0x8a]
    char v63;  // [bp-0x89]
    char v64;  // [bp-0x88]
    char v65;  // [bp-0x87]
    char v66;  // [bp-0x86]
    char v67;  // [bp-0x85]
    char v68;  // [bp-0x84]
    char v69;  // [bp-0x83]
    char v70;  // [bp-0x82]
    char v71;  // [bp-0x78]

    printf("Enter your password: ");
    __isoc99_scanf("%99s", (unsigned int)&v71);
    xor_transform(&v71, 0xffffffaa);
    v0 = 201;
    v1 = 217;
    v2 = 203;
    v3 = 221;
    v4 = 201;
    v5 = 222;
    v6 = 204;
    v7 = 209;
    v8 = 154;
    v9 = 196;
    v10 = 207;
    v11 = 245;
    v12 = 217;
    v13 = 194;
    v14 = 207;
    v15 = 207;
    v16 = 250;
    v17 = 245;
    v18 = 155;
    v19 = 221;
    v20 = 197;
    v21 = 245;
    v22 = 217;
    v23 = 194;
    v24 = 207;
    v25 = 253;
    v26 = 218;
    v27 = 245;
    v28 = 152;
    v29 = 194;
    v30 = 216;
    v31 = 207;
    v32 = 207;
    v33 = 245;
    v34 = 159;
    v35 = 194;
    v36 = 207;
    v37 = 207;
    v38 = 193;
    v39 = 217;
    v40 = 245;
    v41 = 245;
    v42 = 245;
    v43 = 245;
    v44 = 245;
    v45 = 208;
    v46 = 245;
    v47 = 245;
    v48 = 245;
    v49 = 208;
    v50 = 208;
    v51 = 208;
    v52 = 245;
    v53 = 245;
    v54 = 245;
    v55 = 245;
    v56 = 245;
    v57 = 208;
    v58 = 208;
    v59 = 208;
    v60 = 208;
    v61 = 208;
    v62 = 208;
    v63 = 245;
    v64 = 245;
    v65 = 245;
    v66 = 245;
    v67 = 210;
    v68 = 197;
    v69 = 216;
    v70 = 215;
    if (!strcmp(&v71, &v0))
    {
        puts("Correct!");
        return 0;
    }
    puts("Access denied.");
    return 0;
}

long long __libc_csu_init(unsigned int a0, unsigned long long a1, unsigned long long a2, unsigned int a3, unsigned int a4, unsigned int a5)
{
    char v0;  // [bp-0x30]
    char v1;  // [bp-0x20]
    char v2;  // [bp-0x18]
    char v3;  // [bp-0x10]
    char v4;  // [bp-0x8]
    char v5;  // [bp+0x0]
    unsigned long long v8;  // rdi
    void* v12;  // rbx
    unsigned long long v13;  // rax

    if (false)
        return _init(v8, a1, a2, a3, a4, a5, *((long long *)&v0), &v5, *((long long *)&v1), *((long long *)&v2), *((long long *)&v3), *((long long *)&v4));
    v12 = 0;
    do
    {
        v13 = *((long long *)(6294936 + rbx<8> * 8))(v8, a1, a2);
        v12 += 1;
    } while (v12 != 1);
    return v13;
}

long long __libc_csu_fini()
{
    unsigned long v1;  // rax

    return v1;
}

long long _fini()
{
    unsigned long v1;  // rax

    return v1;
}

