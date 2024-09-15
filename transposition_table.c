#include <stdio.h>
#include <stdint.h>

#define ENTRY_SIZE 32
#define TABLE_SIZE (512 * 1024 * 1024 / ENTRY_SIZE)

typedef struct {
    uint64_t zobrist_hash; 
    uint8_t start_row; uint8_t start_col; uint8_t end_row; uint8_t end_col;
    uint8_t flag;  uint8_t score; uint8_t depth;
} TranspositionEntry;
TranspositionEntry transposition_table[TABLE_SIZE];

void store(uint32_t index, uint64_t zobrist_hash, uint8_t start_row, uint8_t start_col, uint8_t end_row, uint8_t end_col, uint8_t flag, uint8_t score, uint8_t depth) {
    TranspositionEntry *entry = &transposition_table[index];
    entry->zobrist_hash = zobrist_hash;
    entry->start_row = start_row; entry->start_col = start_col; entry->end_row = end_row; entry->end_col = end_col;
    entry->flag = flag; entry->score = score; entry->depth = depth;
}

TranspositionEntry* retrieve(uint32_t index, uint64_t zobrist_hash) {
    TranspositionEntry *entry = &transposition_table[index];
    if (entry->zobrist_hash == zobrist_hash) {
        return entry;
    }
    return NULL;
}