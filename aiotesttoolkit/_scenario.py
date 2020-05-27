""" Tools to run a test scenario and control its execution """

class Scenario(object):
    def enter(self, node, *, context=None):
        print("entered ", node)

    def exit(self, node, *, context=None):
        print("exited ", node)

    def with_node(self, node, *, context=None):
        def decorator(fun):
            def wrapper(*args, **kwargs):
                try:
                    self.enter(node, context=context)
                    return fun(*args, **kwargs)
                finally:
                    self.exit(node, context=context)

            return wrapper

        return decorator
