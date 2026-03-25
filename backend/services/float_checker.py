"""
SJDAS v2 - Weave Matrix Float Checker

Validates Jacquard loom bitmap/matrix representations to ensure
optimal thread interlacing (no excessively long floats).
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)

def check_floats(binary_matrix: np.ndarray, max_float: int = 15) -> dict:
    """
    Analyzes a 2D binary numpy array (0=weft face, 1=warp face)
    and identifies continuous horizontal (weft) and vertical (warp) floats
    that exceed the max_float limit.
    
    Returns:
    {
        "status": "PASS" | "FAIL",
        "max_warp_float": int,
        "max_weft_float": int,
        "failures": [
            {"type": "warp|weft", "length": int, "coords": [x, y]}
        ]
    }
    """
    if not isinstance(binary_matrix, np.ndarray):
        binary_matrix = np.array(binary_matrix)
        
    h, w = binary_matrix.shape
    failures = []
    
    max_warp = 0
    max_weft = 0

    # 1. Check Weft Floats (Horizontal 0s)
    for y in range(h):
        row = binary_matrix[y, :]
        padded = np.pad(row, (1, 1), mode='constant', constant_values=1)
        # Find 0s (weft face)
        diffs = np.diff(padded)
        starts = np.where(diffs == -1)[0]
        ends = np.where(diffs == 1)[0]
        
        lengths = ends - starts
        if len(lengths) > 0:
            row_max = np.max(lengths)
            max_weft = max(max_weft, row_max)
            
            # Record failures
            for i, length in enumerate(lengths):
                if length > max_float:
                    failures.append({
                        "type": "weft",
                        "length": int(length),
                        "coords": [int(starts[i]), y]
                    })

    # 2. Check Warp Floats (Vertical 1s)
    for x in range(w):
        col = binary_matrix[:, x]
        padded = np.pad(col, (1, 1), mode='constant', constant_values=0)
        # Find 1s (warp face)
        diffs = np.diff(padded)
        starts = np.where(diffs == 1)[0]
        ends = np.where(diffs == -1)[0]
        
        lengths = ends - starts
        if len(lengths) > 0:
            col_max = np.max(lengths)
            max_warp = max(max_warp, col_max)
            
            # Record failures
            for i, length in enumerate(lengths):
                if length > max_float:
                    failures.append({
                        "type": "warp",
                        "length": int(length),
                        "coords": [x, int(starts[i])]
                    })

    status = "PASS" if len(failures) == 0 else "FAIL"
    
    # Cap reported failures to prevent massive JSON payloads
    reported_failures = failures[:100]
    if len(failures) > 100:
        logger.warning(f"Float check found {len(failures)} failures. Truncating to 100.")
        
    return {
        "status": status,
        "max_warp_float": int(max_warp),
        "max_weft_float": int(max_weft),
        "total_violations": len(failures),
        "failures": reported_failures
    }

def auto_fix_floats(binary_matrix: np.ndarray, max_float: int = 15) -> np.ndarray:
    """
    Attempts to automatically stitch long floats by flipping pixels 
    at the midpoint of violating spans.
    """
    fixed = binary_matrix.copy()
    h, w = fixed.shape
    
    # Fix Weft Floats (0s)
    for y in range(h):
        count = 0
        for x in range(w):
            if fixed[y, x] == 0:
                count += 1
                if count >= max_float:
                    fixed[y, x] = 1 # Stitch
                    count = 0
            else:
                count = 0
                
    # Fix Warp Floats (1s)
    for x in range(w):
        count = 0
        for y in range(h):
            if fixed[y, x] == 1:
                count += 1
                if count >= max_float:
                    fixed[y, x] = 0 # Stitch
                    count = 0
            else:
                count = 0
                
    return fixed
