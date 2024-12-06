import DBcm

creds = {
    "host": "localhost",
    "user": "gofishuser",
    "password": "gofishpasswd",
    "database": "gofishDB",
}

SQL_SELECT = "SELECT username, score, time FROM scores ORDER BY score DESC LIMIT 10"
SQL_INSERT = "INSERT INTO scores (username, score) VALUES (%s, %s)"

def get_top_scores():
    with DBcm.UseDatabase(creds) as db:
        db.execute(SQL_SELECT)
        results = db.fetchall()
        return results
    
def add_scores(username, score):
    with DBcm.UseDatabase(creds) as db:
        db.execute(SQL_INSERT,(username, score))