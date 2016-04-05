from utils import add_cmd
from math import *

variables = {'__builtins__':None, 'pi':pi}
functions = {'__builtins__':None, 'acos':acos, 'asin':asin, 'atan':atan, 'atan2':atan2, 'ceil':ceil, 'cos':cos, 'cosh':cosh, 'degrees':degrees,
'exp':exp, 'fabs':fabs, 'floor':floor, 'fmod':fmod, 'frexp':frexp, 'hypot':hypot, 'ldexp':ldexp, 'log':log, 'log10':log10, 'modf':modf,
'pow':pow, 'radians':radians, 'sin':sin, 'sinh':sinh, 'sqrt':sqrt, 'tan':tan, 'tanh':tanh}

result = '';
        
@add_cmd
def calc(irc, source, msgtarget, args):
    try:
        set_timeout(math, (args, ), {}, 0.5)
        irc.msg(msgtarget, result)
    except (TypeError, ValueError, NameError) as e:
        irc.msg(msgtarget, "Evaluation error");
        
def set_timeout(func, args, kwargs, time):
    p = Process(target=func, args=args, kwargs=kwargs)
    p.start()
    p.join(time)
    if p.is_alive():
        p.terminate()
        return False
    return True
    
def math(expression):
    result = eval(expression, variables, functions)
    return result
