class PaymentErrorException(Exception):
    """
    Raised when there is an error with payment
    """

    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
