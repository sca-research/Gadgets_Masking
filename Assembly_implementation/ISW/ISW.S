.syntax unified
.cpu cortex-m3
.thumb

.section .data

.extern Mask_ORD    @@@@ share_n = Mask_ORD + 1 
.extern share_n
.extern rnd_n       @@@@ The number of Randomness which is the input of the Seminal_ISW multiplication
.extern table       @@@@ Table is used for gfmult

@@@@ defining an array for randomnesses with ROW ORDER method: r[share_n][share_n]
@@@@ each row of the array starts from a memory location  like: mem_addr + share_n  
.balign 1 
rand: .skip rnd_n


.text

@@@@ void Seminal_ISW(uint8_t* input_a, uint8_t* input_b,uint8_t* rnd, uint8_t* c);
.global Seminal_ISW
.func Seminal_ISW

Seminal_ISW:
	push {lr}
	push {r0-r7,r11, r12}  @ input_a:r0, input_b:r1, rnd:r2, c:r3, r12: loop counter i, r11: loop counter j
	

@@@@@ Making the array rand @@@@@@@@@@@@@@@@@

    mov  r12, #0  @ Loop counter i //not MOVS, r12 is Hi reg
for_loop1_i_rnd:
@@@@ r[i][i]=0
@@@@ First: Computing the location of [i][i] in the memory row = (i * (share_n+1)) 
    ldr  r5, =rand  
    adds r4, #1, #share_n 
    mul  r4, r12        @ r4 = r12 * r4 = i*(share_n +1)
    movs r6, #0
    strb r6, [r5, r4]   @ r[i][i]=0


    mov  r11, #0  @ Loop counter j //not MOVS, r11 is Hi reg
for_loop2_j_rnd:
    add  r11, r12, #1 @ Loop counter j: i+1

    @@@@ First: Computing int index = (i * share_n) - (i * (i + 1) / 2) + j - i - 1;
    @@@@ For making the elements of array rand (r[i][j], and r[j][i])
    movs r4, #share_n 
    mul  r4, r12    @ r4 = r12 * r4 = i*share_n 

    mov  r5, r12    @ r5 = i
    adds r5, #1     @ r5 = i+1
    mul  r5, r12    @ r5 = i *(i+1)
    lsrs r5, #1     @ r5 = i*(i+1)/2
    subs r4, r5     @ (i * share_n) - (i * (i + 1) / 2)
    adds r4, r11    @ (i * share_n) - (i * (i + 1) / 2) + j
    sub  r4, r12    @ (i * share_n) - (i * (i + 1) / 2) + j -i
    subs r4, #1     @@@@ r4 = index


    @@@@ Second: Making the elements of array rand (r[i][j], and r[j][i])
    @ r4 is the index
    ldr  r5, =rand  
    ldrb r6, [r2, r4]    @@@@ acces to rnd[index] @@@@  rnd is in r2 which is the input of Seminal_ISW

    @@@@ r[i][j]: finding the right memory location 
    @@@@ r4 = (share_n*i + j): next memory location   
    movs r4, #share_n   @ r4 = share_n
    mul  r4, r12        @ r4 = share_n * i
    adds r4, r11        @ r4 = (share_n*i + j)

    @@@@ store rnd[inedx] into array rand in the location (share_n*i + j): r[i][j]
    strb r6, [r5, r4]

    @@@@ r[j][i]: finding the right memory location
    @@@@ r4 = (share_n*j + i): next memory location   
    movs r4, #share_n   @ r4 = share_n
    mul  r4, r11        @ r4 = share_n * j
    adds r4, r12        @ r4 = (share_n*j + i)


    ldrb r0, [r0, r12]     @ a[i]: input_a is the first input of Seminal_ISW and goes to r0
    ldrb r1, [r1, r11]     @ b[j]: input_b is the second input of Seminal_ISW and goes to r1
    bl   gfmul 	           @ the output is input_a[i]*input_b[j] and is in r0
    eors r6, r0            @ r[i][j] ^ (input_a[i]*input_b[i])
    
    ldrb r0, [r0, r11]     @ a[j]: input_a is the first input of Seminal_ISW and goes to r0
    ldrb r1, [r1, r12]     @ b[i]: input_b is the second input of Seminal_ISW and goes to r1
    bl   gfmul 	           @ the output is input_a[j]*input_b[i] and is in r0	
    eors r6, r0            @ r6 = r[i][j] - (r[i][j] ^ (input_a[i]*input_b[i]))^ gfMul(input_a[j], input_b[i]);

    @@@@ store rnd[inedx] into array rand in the location (share_n*i + j): r[j][i]
    strb r6, [r5, r4]


@@@@ Updating loop counter j @@@@ j < Mask_ord+1; j++
	adds r11, #1  
	cmp  r11, #share_n
    ble for_loop2_j_rnd

@@@@ Updating loop counter (i) @@@@ i < Mask_ord+1; i++
	adds r12, #1  
	cmp  r12, #share_n
    ble  for_loop1_i_rnd



    mov  r12, #0  @ Loop counter i //not MOVS, r12 is Hi reg
for_loop3_i: 

@@@@ First: Computing  c[i]= gfMul(input_a[i], input_b[i]);  c: r3
    ldrb r0, [r0, r12]     @ a[i]: input_a is the first input of Seminal_ISW and goes to r0
    ldrb r1, [r1, r12]     @ b[j]: input_b is the second input of Seminal_ISW and goes to r1
    bl   gfmul 	           @ the output is input_a[i]*input_b[j] and is in r0
    strb r0, [r3, r12]    


    mov  r11, #0  @ Loop counter j //not MOVS, r11 is Hi reg
for_loop4_j:
    add  r11, #1 @ Loop counter j++
    cmp  r11, r12
    bne  c_xor_r


@@@@ Updating loop counter j @@@@ j < Mask_ord+1; j++
	adds r11, #1  
	cmp  r11, #share_n
    ble for_loop4_j

@@@@ Updating loop counter (i) @@@@ i < Mask_ord+1; i++
	adds r12, #1  
	cmp  r12, #share_n
    ble  for_loop3_i

c_xor_r:
    @@@@ Finding the memory location of r[i][j] (rand array) in the memory low: (i * sahre_n)+j
    ldr  r5, =rand  

    movs r4, #share_n
    mul  r4, r12    @ i * sahre_n
    adds r4, r11    @ (i * sahre_n)+j

    @@@@  c[i] = c[i] ^ r[i][j];
    ldrb r6, [r5, r4]   @ r[i][j]
    ldrb r7, [r3, r12]  @ c[i]
    eors r6, r7
    strb r6, [r3, r12]
    bx   lr


    
    
    pop	 {r0-r7,r11, r12}
	pop	 {pc}
.endfunc
.end




@@@@ uint8_t gfmul(uint8_t a, uint8_t b); For calculating: input_a[i] * input_b[j]
@@@@ a: r0, b: r1
.global gfmul
.func gfmul
gfmul:
	push	 {lr} 
	push	 {r0-r5}

    ldr  r2, =table

    ldrb r3, [r2, r0]   @ table[a]
    ldrb r4, [r2, r1]   @ table[b]

    add  r4, r3          @ r4: s = table[a] + table[b]

    @@@@ computing alog: s = table[s+256]; : 256 is more than one byte, split: 255 + 1
    add  r2, #255
    add  r2, #1
    ldrb r3, [r2, r4]   @ [r2, r4] = s + 256, r3: table[s+256]

    @@@@ Checking a = 0 or b = 0
    @@@@ if (a == 0 or b == 0){s = 0;} else {s =  table[s+256]);   if a = 0 or b = 0, then a * b = 0
    ldrb r4, [r2, r0]   @ r4 = a
    ldrb r5, [r2, r1]   @ r5 = b
    mul  r4, r5         @ r4 = a * b
    cmp  r4, #0
    beq  zero_out       @ r0 (output of gfmul) = s = 0
    mov  r0, r4

    @@@@ if (b == 0){s = 0;} else {s =  table[s+256]);  
    ldrb r4, [r2, r1]
    cmp  r4, #0
    beq  zero_out    @ r0 (output of gfmul) = s = 0
    mov  r0, r3


    zero_out:
        mov  r0, #0
        bx   lr


	pop	{r0,r5}
	pop	{pc}
.endfunc
.end



