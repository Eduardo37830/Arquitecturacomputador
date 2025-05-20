class ALU:
    def __init__(self):
        self.flags = {'Z': 0, 'C': 0, 'S': 0, 'O': 0}

    def _update_flags(self, result, carry=0, overflow=0):
        self.flags['Z'] = int(result == 0)
        self.flags['S'] = int((result & (1 << 7)) != 0)  # Asumiendo 8 bits
        self.flags['C'] = carry
        self.flags['O'] = overflow

    def add(self, a, b):
        result = a + b
        carry = int(result > 0xFF)
        overflow = int(((a ^ result) & (b ^ result) & 0x80) != 0)
        result &= 0xFF
        self._update_flags(result, carry, overflow)
        return result

    def sub(self, a, b):
        result = a - b
        carry = int(a < b)
        overflow = int(((a ^ b) & (a ^ result) & 0x80) != 0)
        result &= 0xFF
        self._update_flags(result, carry, overflow)
        return result

    def logical_and(self, a, b):
        result = a & b
        self._update_flags(result)
        return result

    def logical_or(self, a, b):
        result = a | b
        self._update_flags(result)
        return result

    def logical_xor(self, a, b):
        result = a ^ b
        self._update_flags(result)
        return result

    def shift_left(self, a, n=1):
        result = (a << n) & 0xFF
        carry = int((a << n) > 0xFF)
        self._update_flags(result, carry)
        return result

    def shift_right(self, a, n=1):
        result = (a >> n) & 0xFF
        carry = int((a & ((1 << n) - 1)) != 0)
        self._update_flags(result, carry)
        return result

    def complement(self, a):
        result = (~a) & 0xFF
        self._update_flags(result)
        return result

