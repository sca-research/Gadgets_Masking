.syntax unified
.cpu cortex-m3
.thumb

.section .data

.extern Mask_ORD
.extern rnd_n
.extern table @@@@ Table is used for gfmult

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
	
    mov  r12, #0  @ Loop counter i //not MOVS, r12 is Hi reg
loop1_i:
	ldrb r4, [r0, r12]     @ input_a is the first  input and goes to r0
	ldrb r5, [r1, r12]     @ input_b is the second input and goes to r1
	and	 r6, r4, r5 	   @ input_a[i]*input_b[i]
	strb r6, [r3, r12]     @ c=ab goes to r3
	


@@@@ Updating loop counter (i) @@@@ i < Mask_ord+1; i++
	add r12, #1  
	cmp	r12, #share_n
    ble loop1_i


    mov r11, #0
loop2_j:
    add  r11, r12, #1 @ Loop counter j

    @@@@ Computing int index = (i * share_n) - (i * (i + 1) / 2) + j - i - 1;
    mul  r4, r12 @r4 = r12 * r4 = i*share_n 

    mov  r5, r12 @r5 = i
    adds r5, #1 @r5 = i+1
    mul  r5, r12 @r5 = i *(i+1)
    lsrs r5, #1 @r5 = i*(i+1)/2
    subs r4,r5
    add  r4, r11
    sub  r4, r12
    subs r4, #1   @@@@ r4 = index



    @@@@ Making the array rand
    ldr  r5, =rand  
   	ldrb r6, [r2, r4]    @@@@ acces to rnd[index] @@@@  rnd:r2

    @@@@ r[i][j]
    @@@@ r4 + (share_n*i + j): next memory location   
    mul  r4, r12, #share_n
    add  r4, r11    

    @@@@ store rnd[inedx] into array rand : r[i][j]
	strb r6, [r5, r4]

    @@@@ r[j][i]
    @@@@ r4 + (share_n*j + i): next memory location   
    mul  r4, r11, #share_n
    add  r4, r12 

    @@@@ store rnd[inedx] into array rand : r[j][i]
	strb r6, [r5, r4]




@@@@ Updating loop counter j @@@@ j < Mask_ord+1; j++
	add r11, #1  
	cmp	r11, #share_n
    ble loop1_j




for_loop_i:
	add  r12, #1
	cmp	 r12, #share_n
	bne	
    bx	  lr
    
    
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
        .end


	pop	{r0,r5}
	pop	{pc}
.endfunc
.end



