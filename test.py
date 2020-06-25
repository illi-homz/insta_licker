import db_objects as db


session = db.connect_db(db.DB_PATH)

def get_count_folowers():
    session = db.connect_db()
    count = session.query.filter(db.CompleteFolower).count()
    return count


count = get_count_folowers()
print(count)