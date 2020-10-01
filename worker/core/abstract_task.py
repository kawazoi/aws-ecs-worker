class AbstractTask(object):
    @staticmethod
    def run(task_id: str, payload: dict):
        """
        This is the message processing function, it should return an expression that evaluates to 'truthful' (a dict, an array or any object reference) in case of success
        or falsy (None, False, 0.0, 0)  in case of failure.
        Exception handling must be done explicitly.
        This function will be executed in a separate thread, so avoid referencing objects from the main thread inside this scope.
        """
        raise NotImplementedError()
