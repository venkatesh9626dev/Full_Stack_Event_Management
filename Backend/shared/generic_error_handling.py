from sqlalchemy.exc import (
    OperationalError,
    SQLAlchemyError,
    IntegrityError,
    ProgrammingError,
)


# Need to implement logging


class Generic_Error_Handling:

    @staticmethod
    def db_exception_handling(e: SQLAlchemyError):

        if isinstance(e, OperationalError):

            return {"message": "Database Connection Error", "details": str(e.orig)}

        elif isinstance(e, IntegrityError):

            return {"message": "Table Constraint Error", "details": str(e.orig)}

        elif isinstance(e, ProgrammingError):

            return {"message": "SQL Query Error", "details": str(e.statement)}

        elif isinstance(e, SQLAlchemyError):

            return {"message": "Generic Database Error", "details": str(e.args)}

        return {"message": "An unexpected Error", "details": str(e)}
