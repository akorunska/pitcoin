from .stack import Stack


def run_script(code: str, msg):
    cur = 0
    stack = Stack()
    while cur < len(code):
        opcode = int(code[cur:cur+2], 16)
        cur += 2
        if 1 <= opcode <= 75:
            data = code[cur:cur + opcode*2]
            cur += opcode*2
            stack.push(data)
        if opcode == 118:
            stack.op_dup()
        if opcode == 169:
            stack.op_hash160()
        if opcode == 136:
            if not stack.op_equal_verify():
                return False
        if opcode == 172:
            stack.op_checksig(msg)
    return stack.running_succeeded()

