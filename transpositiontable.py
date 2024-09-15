import ctypes
import psutil
import os
from ctypes import c_uint64, c_uint8, c_uint32, Structure, CDLL, POINTER

lib = CDLL('./libtransposition_table.so')
class TranspositionEntry(Structure):
    _fields_ = [
        ('zobrist_hash', c_uint64),
        ('start_row',c_uint8), ('start_col',c_uint8),('end_row',c_uint8),('end_col',c_uint8),
        ('flag', c_uint8),('score', c_uint8),('depth', c_uint8),
    ]

lib.store.argtypes = [c_uint32, c_uint64, c_uint8, c_uint8, c_uint8,c_uint8, c_uint8, c_uint8, c_uint8]
lib.store.restype = None
lib.retrieve.argtypes = [c_uint32, c_uint64]
lib.retrieve.restype = POINTER(TranspositionEntry)

def store_entry(index, zobrist_hash, start_row, start_col, end_row, end_col, flag, score, depth):
    lib.store(index, zobrist_hash, start_row, start_col, end_row, end_col, flag, score, depth)

def retrieve_entry(index, zobrist_hash):
    entry_ptr = lib.retrieve(index, zobrist_hash)
    if entry_ptr:
        return entry_ptr.contents
    return None

