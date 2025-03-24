from database import SessionLocal

class Base_Dao:
    
    session = SessionLocal
    
    def __init__(self, model):
        self.model = model
        
    
    def fetch_record(self,field_name,field_value):
        """ can be used for fetching single record. For eg: Fetching events by the event id providing field name(event_id) and field_value(12345).

        Args:
            field_name (_type_): Field name of the model
            field_value (_type_): Field value of the selected Field

        Returns:
            _type_: Returns the column and value as a dictionary
        """        

        with Base_Dao.session() as db:
            
            record_object = db.query(self.model).filter(getattr(self.model,field_name) == field_value).first()
            
            return record_object.__dict__ if record_object else None
        
    def fetch_records(self,field_name,field_value):
        """ can be used for fetching records by . For eg: Filtering paid events by providing field name(ticket_type) and field_name(free).

        Args:
            field_name (_type_): Field name of the model
            field_value (_type_): Field value of the selected Field

        Returns:
            _type_: Returns the column and value as a dictionary
        """        
        with Base_Dao.session()  as db:
            
            records_object_list = db.query(self.model).filter(getattr(self.model,field_name) == field_value).all()
                
            if not records_object_list:
                return []
            
            records_list = [record.__dict__ for record in records_object_list]
            
            return records_list
    