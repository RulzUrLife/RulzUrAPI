
def expression_assert(fn, expression):
    (expression_arg,), _ = fn.call_args
    return expression_arg.__dict__ == expression.__dict__
