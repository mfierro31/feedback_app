from app import app
from models import User, db, Feedback

db.drop_all()
db.create_all()

u1 = User.register("NoobNoob", "gotdamn", "noobnoob@gmail.com", "Noob", "Noob")
u2 = User.register("PoopyButthole", "ooh-wee", "poop_butt@hotmail.com", "Poopy", "Butthole")
u3 = User.register("GetRicked", "wubba-lubba", "rick_sanchez@yahoo.com", "Rick", "Sanchez")
u4 = User.register("SloMo", "bro", "slow_mobius@gmail.com", "Slow", "Mobius")
u5 = User.register("MorT", "ahh-geez", "morty_s@gmail.com", "Morty", "Smith")

db.session.add_all([u1, u2, u3, u4, u5])
db.session.commit()

f1 = Feedback(title="Good Site", content="I like it.  Not too complex.  Short, sweet, and to the point.", username="NoobNoob")
f2 = Feedback(title="Ehh...", content="What am I supposed to do other than view my own information?  Borrrriiiiinng!  Who made this site?  Jerry Smith?", username="GetRicked")
f3 = Feedback(title="Sweet Site Bro!", content="Ha haaaaa!  Hey duuuuude, I don't care if your site is boring, brohhhhhh!", username="SloMo")
f4 = Feedback(title="Good site for my recovery", content="Ooooooooh-weeeee!  This site is perfect for my slow, boring recovery!  Thanks!", username="PoopyButthole")
f5 = Feedback(title="Ah, Geez, Man...", content="Hey dawg, not to rain on your parade, but this site's lame, yo.  Make it more fun...y'know?", username="MorT")

db.session.add_all([f1, f2, f3, f4, f5])
db.session.commit()