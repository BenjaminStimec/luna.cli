NONE    = "\033[00m"
BLUE    = "\033[34m"
RED     = "\033[31m"

def color_text(color, val):
    return(f"{color}{val}\033[00m")

def sys_print(val):
    print(color_text(BLUE, val))
    return

def err_print(val):
    print(color_text(RED, val))
    return
