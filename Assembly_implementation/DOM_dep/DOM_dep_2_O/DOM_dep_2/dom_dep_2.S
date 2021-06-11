
  .syntax unified
  .text
  .thumb
  
  .extern table       @@@@ table is used for gfmult
  
@@@@ extern void Dom_indep_2(uint8_t* inputa: addres: r0, uint8_t* inputb: address: r1, uint8_t* rnd: address: r2, uint8_t* output: address: r3);
@inputa: a0, a1, a2, inputb: b0, b1, b2, rnd: rnd0-rnd6, output: c: c0, c1, c2
@ (z0, z1, z2) = (rnd0, rnd1, rnd2); randomness for DOM_indep (rand0, rand1, rand2) = (rnd3, rnd4, rnd5)

.global Dom_dep_2
.func Dom_dep_2
Dom_dep_2:
  push  {lr}
  push  {r4-r11}

@@@@@ r0 = &a, r1 = &b, r2 = &rand, r3 = &c

@@@@@ Saving r3 (the address of the output)
  mov  r11, r3    @ r11 = &c

@@@@@ Saving r2 (the address of the input rnd)
  mov  r10, r2     @ r10 = &rand

@@@@@ Saving r1 (the address of the input b)
  mov  r9, r1    @ r9 = &b

@@@@@ Saving r0 (the address of the input a)
  mov  r8, r0    @ r8 = &a

@@@@@ Loading arguments @@@@@@@@@@@@
  ldrb r4, [r0, #0] @ r4 = a0; r0 = &a, r1 = &b, r2 = &rand, r3 = &c
  ldrb r5, [r0, #1] @ r5 = a1; r0 = &a, r1 = &b, r2 = &rand, r3 = &c
  ldrb r6, [r2, #0] @ r6 = z0; r0 = &a, r1 = &b, r2 = &rand, r3 = &c
  ldrb r7, [r2, #1] @ r7 = z1; r0 = &a, r1 = &b, r2 = &rand, r3 = &c
  ldrb r2, [r2, #2] @ r2 = z2; r0 = &a, r1 = &b, r2 = z2  , r3 = &c


@@@@@@@@@@ Computing: ai * bi
@@@@@@ In gfmul, r0 and r1 are the arguments
@@@@ a0 * z0
  mov  r0, r4   @ r0 = a0
  mov  r1, r6   @ r1 = z0
  bl   gfmul    @ r0 = a0 * z0
  
  strb r0, [r3, #0] @ Storing (a0 * z0) in c0

@@@@ a1 * z1
  mov  r0, r5   @ r0 = a1
  mov  r1, r7   @ r1 = z1
  bl   gfmul    @ r0 = a1 * z1

  strb r0, [r3, #1] @ Storing (a1 * z1) in c1

@@@@ a2 * z2
  mov  r0, r8       @ r0 = &a
  ldrb r0, [r0, #2] @ r0 = a2
  mov  r1, r2       @ r1 = z2
  bl   gfmul        @ r0 = a2 * z2
  
  strb r0, [r3, #2] @ Storing (a2 * z2) in c2


@@@@@@@@@@ Computing: The outputs of DOM_independent ci = a * z 

@From previous step: 
@@@@ r2 = z2, r3 = &c, r4 = a0, r5 = a1, r6 = z0
@@@@ r7 = z1, r8 = &a, r9 = &b, r10 = &rand, r11 = &c

@@@@ c0 = (a0 * z0) ^ [(a0 * z1) ^ rand0] ^ [(a0 * z2) ^ rand1]
  mov  r0, r4         @ r0 = a0
  mov  r1, r7         @ r1 = z1
  bl   gfmul          @ r0 = a0 * z1

  mov  r3, r2         @ r3 = z2
  mov  r2, r10        @ r2 = &rand
  ldrb r7, [r2, #3]   @ r7 = rand0 // r7 = z1, for computing c1, z1 (alone) is not needed, so, r7 can be used here
  mov  r10, r7        @ r10 = rand0    @ Saving for using in C1
  eors r7, r0         @ r7 = [(a0 * z1) ^ rand0] 

  mov  r0, r4         @ r0 = a0
  mov  r1, r3         @ r1 = z2
  bl   gfmul          @ r0 = a0 * z2

  ldrb r1, [r2, #4]   @ r1 = rand1
  eors r1, r0         @ r1 = [(a0 * z2) ^ rand1]
  
  mov  r4, r3         @ r4 = z2   @ a0 in r4 is not needed in c1, Saving z2 for using in C1
  mov  r3, r11        @ r3 = &c
  ldrb r0, [r3, #0]   @ r0 = a0 * z0

  eors r0, r7         @ r0 = (a0 * z0) ^ [(a0 * z1) ^ rand0]
  eors r1, r0         @ r1 = (a0 * z0) ^ [(a0 * z1) ^ rand0] ^ [(a0 * z2) ^ rand1]


  strb r1, [r3, #0]   @ Storing the output of DOM_independent c0 in c0


@From previous step: 
@@@@ r2 = &rand, r3 = &c, r4 = z2, r5 = a1, r6 = z0
@@@@ r7 = , r8 = &a, r9 = &b, r10 = rand0, r11 = &c

@@@@ c1 = [(a1 * z0) ^ rand0] ^ (a1 * z1) ^ [(a1 * z2) ^ rand2]
  mov  r0, r5         @ r0 = a1
  mov  r1, r6         @ r1 = z0
  bl   gfmul          @ r0 = a1 * z0

  mov  r7, r10        @ r7 = rand0
  eors r7, r0         @ r7 = [(a1 * z0) ^ rand0]

  mov  r0, r5         @ r0 = a1
  mov  r1, r4         @ r1 = z2
  bl   gfmul          @ r0 = a1 * z2

  ldrb r5, [r2, #5]   @ r5 = rand2  // r5 = a1, for computing c2, a1 (alone) is not needed, so, r5 can be used here
  mov  r10, r5        @ r10 = rand2

  eors r5, r0         @ r5 = [(a1 * z2) ^ rand2]


  ldrb r0, [r3, #1]   @ r0 = a1 * z1
  eors r0, r7         @ r0 = [(a1 * z0) ^ rand0] ^ (a1 * z1) 
  eors r0, r5         @ r0 = c1 = [(a1 * z0) ^ rand0] ^ (a1 * z1) ^ [(a1 * z2) ^ rand2]
  
  
  strb r0, [r3, #1]   @ Storing the output of DOM_independent c1 in c1

@From previous step: 
@@@@ r2 = &rand, r3 = &c, r4 = z2, r5 = , r6 = z0
@@@@ r7 = , r8 = &a, r9 = &b, r10 = rand2, r11 = &c

@@@@ c2 = [(a2 * z0) ^ rand1] ^ [(a2 * z1) ^ rand2] ^ (a2 * z2)
  mov  r0, r8         @ r0 = &a
  ldrb r5, [r0, #2]   @ r5 = a2
  ldrb r4, [r2, #1]   @ r4 = z1
  ldrb r7, [r2, #4]   @ r7 = rand1

  mov  r0, r5         @ r0 = a2
  mov  r1, r6         @ r1 = z0
  bl   gfmul          @ r0 = a2 * z0

  eors r7, r0         @ r7 = [(a2 * z0) ^ rand1]

  mov  r0, r5         @ r0 = a2
  mov  r1, r4         @ r1 = z1
  bl   gfmul          @ r0 = a2 * z1

  mov  r5, r10        @ r5 = rand2 // r5 = a2; for computing x, a2 is not needed
  mov  r10, r2        @ r10 = &rand
  eors r5, r0         @ r4 = [(a2 * z1) ^ rand2]

  ldrb r0, [r3, #2]   @ r0 = a2 * z2
  
  eors r5, r7         @ r4 = [(a2 * z0) ^ rand1] ^ [(a2 * z1) ^ rand2]

  eors r0, r5         @ r0 = [(a2 * z0) ^ rand1] ^ [(a2 * z1) ^ rand2] ^ (a2 * z2)

 
  @mov  r3, r11
  strb r0, [r3, #2]    @ Storing  the output of DOM_independent c2 in c2
  
  
@@@@@@@@@@ Computing: x = (z0 ^ b0) ^ (z1 ^ b1) ^ (z2 ^ b2)
@From previous step: 
@@@@ r2 = &rand, r3 = &c, r4 = z1, r5 = , r6 = z0
@@@@ r7 = , r8 = &a, r9 = &b, r10 = &rand, r11 = &c

  mov  r1, r9         @ r1 = &b
  ldrb r5, [r1, #0]   @ r5 = b0
  ldrb r7, [r1, #1]   @ r7 = b1
  ldrb r1, [r1, #2]   @ r1 = b2
  ldrb r0, [r2, #2]   @ r0 = z2

  eors r6, r5         @ z0 ^ b0
  eors r4, r7         @ z1 ^ b1
  eors r1, r0         @ z2 ^ b2

  eors r6, r4         @ (z0 ^ b0) ^ (z1 ^ b1)
  eors r1, r6         @ (z0 ^ b0) ^ (z1 ^ b1) ^ (z2 ^ b2)


@@@@@@@@@@ Computing: the outputs of DOM_depen ci: (ai * x) ^ ci
@From previous step: 
@@@@ r1 = x, r2 = &rand, r3 = &c, r4 = , r5 = b0, r6 = 
@@@@ r7 =  b1, r8 = &a, r9 = &b, r10 = &rand, r11 = &c

  mov  r0, r8         @ r0 = &a
  ldrb r4, [r0, #1]   @ r4 = a1
  ldrb r5, [r0, #2]   @ r5 = a2
  ldrb r0, [r0, #0]   @ r0 = a0


  ldrb r2, [r3, #0]   @ r2 = c0
  ldrb r7, [r3, #1]   @ r7 = c1
  ldrb r3, [r3, #2]   @ r3 = c2

@r0 = a0, r1 = x
  bl   gfmul          @ r0 = a0 * x
  eors r2, r0         @ c0 = (a0 * x) ^ c0


@r1 = x
  mov  r0, r4         @ r0 = a1
  bl   gfmul          @ r0 = a1 * x
  eors r7, r0         @ c1 = (a1 * x) ^ c1


@r1 = x
  mov  r0, r5         @ r0 = a2
  bl   gfmul          @ r0 = a2 * x
  eors r0, r3         @ c2 = (a2 * x) ^ c2


  mov  r3, r11
  strb r2, [r3, #0]    @ Storing the output of DOM_dependent c0 in c0
  strb r7, [r3, #1]    @ Storing the output of DOM_dependent c1 in c1
  strb r0, [r3, #2]    @ Storing the output of DOM_dependent c2 in c2


  pop  {r4-r11}
  pop  {pc}
  .endfunc 




@@@@@ uint8_t gfmul(uint8_t a, uint8_t b); For calculating: input_a[i] * input_b[j]
@@@@@@@@ gfmul(in_r0:a, in_r1: b, out_r0: return)

.global gfmul
.func gfmul
gfmul:
	push	 {r2-r5}

    ldr  r2, =table     @ the address of the  "table"

    ldrb r3, [r2, r0]   @ r3 = table[a] 
    ldrb r4, [r2, r1]   @ r4 = table[b] 
    adds r3, r4         @ r3 = s = table[a] + table[b]

    @@@@ Get the antilog: s = table[s+256]: g ^ s 
    adds r3, #128       @ r3 = s + 128 :s + 256; : 256 is more than one byte, split: 128 + 128
    adds r3, #128       @ r3 = s + 256
    ldrb r4, [r2, r3]   @ r4 = s = table[s+256]

    @@@@ Checking if a = 0 or b = 0, return 0; without conditional branch
    negs r5, r0         @ r5 = -a
    asrs r5, #32        @ r5 = -a >> 8  (4*8=32)
    ands r5, r1         @ r5 = tmp = b & (-a >> 8)
    negs r5, r5         @ r5 = -tmp 
    asrs r5, #32        @ r5 = -tmp >> 8
    ands r4, r5         @ r4 = s & (-tmp >> 8)
    mov  r0, r4

	pop {r2-r5}
	
  bx lr
.endfunc
.end

