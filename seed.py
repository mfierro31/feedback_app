from app import app
from models import User, db

db.drop_all()
db.create_all()

u1 = User.register("NoobNoob", "gotdamn", "noobnoob@gmail.com", "Noob", "Noob")
u2 = User.register("PoopyButthole", "ooh-wee", "poop_butt@hotmail.com", "Poopy", "Butthole")
u3 = User.register("GetRicked", "wubba-lubba", "rick_sanchez@yahoo.com", "Rick", "Sanchez")
u4 = User.register("SloMo", "bro", "slow_mobius@gmail.com", "Slow", "Mobius")

db.session.add_all([u1, u2, u3, u4])
db.session.commit()