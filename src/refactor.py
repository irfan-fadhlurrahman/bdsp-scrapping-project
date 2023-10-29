import pytx

from dataclasses import dataclass
from datetime import datetime

@dataclass
class HargaPanganRataRata:
  url: str
  user_id: str
  db_conn: DatabaseConnection
  file_handler: FileHandler
  table: SQLTableMetadata
  current_date: datetime
  
  
