#include "gfmul.h"
#include "stdint.h"

uint8_t gfMul(uint8_t a, uint8_t b)
{
    int s = 0;
    s = table[a] + table[b]; 
	int q;
    /* Get the antilog */
	s = table[s+256];
	uint8_t z = 0;
    q = s;
    if(a == 0) {
		s = z;
	} else {
		s = q;
    }
	if(b == 0) {
		s = z; 
	} else {
		q = z;
	}
	return s;
}
