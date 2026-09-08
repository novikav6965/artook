import sqlite3
class DataBase:
    def __init__(self):
        self.db_name = 'database.db'
        self.con = None
        self.cursor = None
        self._create_tables()



    def _connect(self):
        self.con = sqlite3.connect(self.db_name)
        self.cursor = self.con.cursor()
        return None

    def _disconnect(self):
        if self.con:
            self.con.close()
        return None

    def _create_tables(self):
        self._connect()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Reports (
                            No INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            id INTEGER,
                            damage TEXT)''')
        self.con.commit()
        self._disconnect()
        return None

    def get_top(self):
        self._connect()
        self.cursor.execute('SELECT No, name, id, damage FROM Reports')
        top = self.cursor.fetchall()
        self._disconnect()
        return top

    def delete_report(self, No):
        self._connect()
        self.cursor.execute('DELETE FROM Reports WHERE No = ?', (No,))
        self.con.commit()
        self.update_num()
        self._disconnect()


    def add_report(self, report):
            # Разбираем строку вида "Братулек (1837439928) - 5ккк"
        try:
            name = report.split('(')[0].strip()
            id_part = report.split('(')[1].split(')')[0].strip()
            damage = report.split('-')[1].strip()

            self._connect()
            self.cursor.execute('INSERT INTO Reports (name, id, damage) VALUES (?, ?, ?)',(name, int(id_part), damage))
            self.con.commit()
            self.update_num()
            self._disconnect()
        except (IndexError, ValueError):
            # Если формат строки неверный
            return False
        return True

    def update_num(self):
        self.cursor.execute('''
                                   UPDATE Reports 
                                   SET No = (
                                       SELECT COUNT(*) 
                                       FROM Reports AS r2 
                                       WHERE r2.No <= Reports.No
                                   )
                               ''')
        self.con.commit()