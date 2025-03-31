from database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError


class Base_Dao:
    session = SessionLocal

    def __init__(self, model):
        self.model = model

    def fetch_record(self, field_name, field_value):
        """can be used for fetching single record. For eg: Fetching events by the event id providing field name(event_id) and field_value(12345).

        Args:
            field_name (_type_): Field name of the model
            field_value (_type_): Field value of the selected Field

        Returns:
            _type_: Returns the column and value as a dictionary
        """

        try:
            with Base_Dao.session() as db:
                record_object = (
                    db.query(self.model)
                    .filter(getattr(self.model, field_name) == field_value)
                    .first()
                )

                return record_object.__dict__ if record_object else None
        except SQLAlchemyError as e:
            raise e

    def fetch_records_by_field_name(self, field_name, field_value):
        """can be used for fetching records by . For eg: Filtering paid events by providing field name(ticket_type) and field_name(free).

        Args:
            field_name (_type_): Field name of the model
            field_value (_type_): Field value of the selected Field

        Returns:
            _type_: Returns the column and value as a dictionary
        """

        try:
            with Base_Dao.session() as db:
                records_object_list = (
                    db.query(self.model)
                    .filter(getattr(self.model, field_name) == field_value)
                    .all()
                )

                if not records_object_list:
                    return []

                records_list = [record.__dict__ for record in records_object_list]

                return records_list
        except SQLAlchemyError as e:
            raise e

    def fetch_records_by_list(self, field_name, field_value_list: list):
        try:
            with Base_Dao.session() as db:
                data_object_list = (
                    db.query(self.model)
                    .filter(getattr(self.model, field_name) in (field_value_list))
                    .all()
                )

                if not data_object_list:
                    return None

                data_list = [data.__dict__ for data in data_list]

                return data_list

        except SQLAlchemyError as e:
            raise e

    def fetch_records_from_model(self):
        """can be used for fetching all records from the model.

        Args:
            field_name (_type_): Field name of the model
            field_value (_type_): Field value of the selected Field

        Returns:
            _type_: Returns the column and value as a dictionary
        """

        try:
            with Base_Dao.session() as db:
                records_object_list = db.query(self.model).all()

                if not records_object_list:
                    return []

                records_list = [record.__dict__ for record in records_object_list]

                return records_list

        except SQLAlchemyError as e:
            raise e

    def create_record(self, data: dict):
        try:
            with Base_Dao.session() as db:
                new_data = self.model(**data)

                db.add(new_data)

                db.commit()

                db.refresh(new_data)

                return new_data.__dict__

        except SQLAlchemyError as e:
            db.rollback()

            raise e

    def update_record(self, data, field_name, field_value):
        try:
            with self.session() as db:
                data_row = (
                    db.query(self.model)
                    .filter(getattr(self.model, field_name) == field_value)
                    .first()
                )

                for key, value in data.items():
                    setattr(data_row, key, value)

                db.commit()

                db.refresh(data_row)

                return data_row.__dict__

        except SQLAlchemyError as e:
            db.rollback()

            raise e
