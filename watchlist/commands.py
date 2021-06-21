import click
from watchlist.models import User, Movie
from watchlist import app, db

# initialize database
@app.cli.command()
@click.option('--drop', is_flag = True, help = "Create after drop")
def initdb(drop):
    """Initialize the database"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized database!")

# Create fake data
@app.cli.command()
@click.option("--forgemovie", prompt = True, help = "Enter 'True': Forge movie data; 'False': Only forge user account")
@click.option("--username", prompt = True, help = "The username used to login")
@click.option("--name", prompt = True, help = "Your name")
@click.option("--password", prompt = True, hide_input = True, confirmation_prompt = True, help = "The password used to login")
def forge(username, name, password, forgemovie):
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    click.echo('Creating user...')
    user = User(name=name, username = username)
    user.set_password("123")
    db.session.add(user)
    if forgemovie:
        click.echo('Forging movies...')
        for m in movies:
            movie = Movie(title=m['title'], year=m['year'], username = username)
            db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


