import unittest
from app import app, db, Movie, User, forge, initdb

class WatchlistTestCase(unittest.TestCase):

    def setUp(self):
        # config update
        app.config.update(
            TESTING = True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        # database
        db.create_all()
        user = User(name = "Test", username = "test")
        user.set_password("123")
        movie = Movie(title = "Test movie title", year = "2021")
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Existence of app
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # Test whether in testing mode
    def test_app_is_testing(self):
        self.assertTrue(app.config["TESTING"])

    # Test 404
    def test_404_page(self):
        response = self.client.get("/nothing")
        data = response.get_data(as_text=True)
        self.assertIn("Page Not Found - 404", data)
        self.assertIn("Go Back", data)
        self.assertEqual(response.status_code, 404)

    # Test home page
    def test_index_page(self):
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        self.assertIn("Test's Watchlist", data)
        self.assertIn("Test movie title", data)
        self.assertEqual(response.status_code, 200)

    # Login
    def login(self):
        self.client.post("/login", data = dict(
            username = "test",
            password = "123"
        ), follow_redirects = True)

    # Test create item
    def test_create_item(self):
        self.login()

        ## Test create
        response = self.client.post("/", data = dict(
            title = "New movie",
            year = "2021"
        ), follow_redirects = True)
        data = response.get_data(as_text=True)
        self.assertIn("Item created.", data)
        self.assertIn("New movie", data)

        ## Test create: title is empty
        response = self.client.post("/", data=dict(
            title="",
            year="2021"
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn("Item created.", data)
        self.assertIn("Invalid input.", data)

        ## Test create: year is empty
        response = self.client.post("/", data=dict(
            title="New movie",
            year=""
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn("Item created.", data)
        self.assertIn("Invalid input.", data)

    # Test update
    def test_update_item(self):
        self.login()

        ## Test update page
        response = self.client.get("/movie/edit/1")
        data = response.get_data(as_text=True)
        self.assertIn('Edit', data)
        self.assertIn('Test movie title', data)
        self.assertIn('2021', data)

        ## Test update
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('2019', data)
        self.assertIn('New Movie Edited', data)

        ## Test update: title empty
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

        ## Test update: year empty
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

    # Test delete item
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test movie title', data)

    # Test login protect
    def test_login_protect(self):
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        self.assertNotIn("Edit", data)
        self.assertNotIn("Delete", data)
        self.assertNotIn("Logout", data)
        self.assertNotIn("Settings", data)
        self.assertNotIn('<form method = "post">',data)

    # Test login
    def test_login(self):
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        ## Wrong password
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        ## Wrong username
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        ## Empty username
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

        ## Empty password
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

    # Test logout
    def test_logout(self):
        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)

    # Test settings
    def test_settings(self):
        self.login()

        ## settings page
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Your Name', data)

        ## settings
        response = self.client.post('/settings', data=dict(
            name='Grey Li',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.', data)
        self.assertIn('Grey Li', data)

        ## settings: name empty
        response = self.client.post('/settings', data=dict(
            name='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated.', data)
        self.assertIn('Invalid input.', data)

    # Test forge
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    # Test initdb
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database!', result.output)

    # Test admin
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'tristal', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'tristal')
        self.assertTrue(User.query.first().validate_password('123'))

    # Test update admin
    def test_admin_command_update(self):
        result = self.runner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'peter')
        self.assertTrue(User.query.first().validate_password('456'))

if __name__ == '__main__':
    unittest.main()
