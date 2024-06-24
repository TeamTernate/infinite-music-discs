class ExceptionWithMessage(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"Save error: {self.message}"


class SaveExceptions:

    class OSError(ExceptionWithMessage):

        def __init__(self):
            super().__init__(
                "Can't save file. This could be due to a permissions error"
            )


class LoadExceptions:
    
    class InvalidVersion(ExceptionWithMessage):

        def __init__(self):
            super().__init__("Invalid save version")

    class OSError(ExceptionWithMessage):

        def __init__(self):
            super().__init__(
                "Can't open save file. This could be due to a permissions error"
            )

    class JSONDecodeError(ExceptionWithMessage):

        def __init__(self):
            super().__init__("Can't decode save file. It is probably corrupted")
