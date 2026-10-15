class IncomeNotFoundError(Exception):
    def __init__(self, income_id: int):
        self.income_id = income_id
        message = f"Income with ID {income_id} was not found."
        super().__init__(message)

class InvalidIncomeOperationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
