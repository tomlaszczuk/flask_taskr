#!/home/tomek/.envs/flask/bin/python
import os
import unittest


from project import app, db, bcrypt
from config import BASE_DIR
from project.models import User, Task

TEST_DB = os.path.join(BASE_DIR, 'test.db')


class TestCase(unittest.TestCase):

    def setUp(self):
        # executes prior to each test
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + TEST_DB
        app.config['DEBUG'] = False
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        # executes after each TestCase
        db.drop_all()

    # ============================= helpers ================================= #
    def login(self, name, password):
        # helper function to keep our code keep DRY
        return self.app.post("/users/login",
                             data=dict(name=name, password=password),
                             follow_redirects=True)

    def register(self, name, email, password):
        return self.app.post("/users/register",
                             data=dict(
                                 name=name, email=email,
                                 password=password,
                                 confirm=password
                             ),
                             follow_redirects=True)

    def create_user(self, name, email, password):
        new_user = User(name=name, email=email,
                        password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

    def create_superuser(self, name, email, password):
        superuser = User(name=name, email=email,
                         password=bcrypt.generate_password_hash(password),
                         role="admin")
        db.session.add(superuser)
        db.session.commit()

    def post_task(self, task_name, due_date="2014/10/20",
                  posted_date='2014/10/11'):
        return self.app.post("/tasks/add", data=dict(name=task_name,
                                                     due_date=due_date,
                                                     posted_date=posted_date,
                                                     priority='10',
                                                     status='1'),
                             follow_redirects=True)

    def create_task(self, task_name, user_id, due_date="2014/10/20",
                    posted_date="2014/10/11"):
        new_task = Task(name=task_name, due_date=due_date,
                        posted_date=posted_date, priority=10, status=1,
                        user_id=user_id)
        db.session.add(new_task)
        db.session.commit()

    def logout(self):
        return self.app.get("/users/logout", follow_redirects=True)
    # ======================================================================= #

    # ============================= test functions ========================== #
    def test_user_set_up(self):
        self.create_user("foobar", "foobar@gmai.com", "foobarfoo")

    def test_user_can_register(self):
        self.register("foouser", "foo@bar.com.pl", "foouser")
        test = db.session.query(User).all()
        self.assertIn("foouser", [elem.name for elem in test])

    def test_registered_user_see_message(self):
        response = self.register("newuser", "newuser@com.pl", "newuser")
        self.assertIn("You have been succesfully registered. Please login",
                      response.data)

    def test_user_cannot_register_unless_all_fields_filled(self):
        response = self.register("fooBar", "foobar@foobar.pl", "")
        self.assertIn('This field is required', response.data)

    def test_form_is_present_on_login_page(self):
        response = self.app.get("/users/login")
        self.assertEquals(response.status_code, 200)
        self.assertIn("Please login to see your tasks", response.data)

    def test_unregister_users_cannot_login(self):
        response = self.login('foo', 'bar')
        self.assertIn("Invalid username or password", response.data)

    def test_register_users_can_login(self):
        self.register(name="foofoofoo", email="foo@com.pl",
                      password="foofoofoo")
        response = self.login(name="foofoofoo", password="foofoofoo")
        self.assertIn("You have succesfully logged in", response.data)

    def test_invalid_form_name(self):
        self.register(name="foofoofoo", email="foo@com.pl",
                      password="foofoofoo")
        response = self.login(name="fofofo", password="foofoofoo")
        self.assertIn("Invalid username or password", response.data)

    def test_invalid_form_password(self):
        self.register(name="foofoofoo", email="foo@com.pl",
                      password="foofoofoo")
        response = self.login(name="foofoofoo", password="fofofo")
        self.assertIn("Invalid username or password", response.data)

    def test_not_logged_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn("You are now logged out. Thank you, come again",
                         response.data)

    def test_logged_users_can_logout(self):
        self.register("tomekfoo", "foobar@bar.pl", "foobar")
        self.login("tomekfoo", "foobar")
        response = self.logout()
        self.assertIn("You are now logged out. Thank you, come again",
                      response.data)

    def test_not_logged_users_cannot_see_tasks(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertIn("You need to login first", response.data)

    def test_users_can_add_task(self):
        self.create_user("FooBar", "foobar@pl.com", "password")
        self.login("FooBar", "password")
        self.app.get("/tasks", follow_redirects=True)
        response = self.post_task("Go to movies")
        self.assertIn("New task has been succesfully added", response.data)

    def test_task_not_added_when_error(self):
        self.create_user("FooBar", "foobar@pl.com", "password")
        self.login("FooBar", "password")
        self.app.get("/tasks", follow_redirects=True)
        response = self.post_task("Go to movies", due_date="")
        self.assertNotIn("New task has been succesfully added", response.data)
        self.assertIn("input date by YYYY/MM/DD (ex. 2014/10/10)",
                      response.data)

    def test_user_can_complete_task(self):
        self.create_user("FooBar", "foobar@pl.com", "password")
        self.login("FooBar", "password")
        self.app.get("/tasks", follow_redirects=True)
        self.post_task("Go to movies")
        response = self.app.get("/tasks/mark/1", follow_redirects=True)
        self.assertIn("Task has been marked as completed", response.data)
        status = db.session.query(Task).all()[0].status
        self.assertEquals(status, 0)

    def test_user_can_delete_task(self):
        self.create_user("FooBar", "foobar@pl.com", "password")
        self.login("FooBar", "password")
        self.app.get("/tasks", follow_redirects=True)
        self.post_task("Go to movies")
        response = self.app.get("/tasks/delete/1", follow_redirects=True)
        self.assertIn("Task has been deleted", response.data)
        task = db.session.query(Task).all()
        self.assertEquals([], task)

    def test_default_user_role(self):
        db.session.add(User("tomek", "tomek@tomek.pl", "tomek123"))
        db.session.commit()
        users = db.session.query(User).all()
        for user in users:
            self.assertEquals(user.role, "user")

    def test_superuser_can_mark_tasks_not_created_by_him(self):
        self.create_user("some_user", "user@email.com", "password")
        self.login("some_user", "password")
        self.app.get("/tasks", follow_redirects=True)
        self.post_task("My ordinary user task")
        self.app.get("/users/logout", follow_redirects=True)
        self.create_superuser("admin", "admin@admin.com", "password")
        self.login("admin", "password")
        self.app.get("/tasks", follow_redirects=True)
        response = self.app.get("/tasks/mark/1", follow_redirects=True)
        self.assertIn("Task has been marked as completed", response.data)
        status = db.session.query(Task).all()[0].status
        self.assertEquals(status, 0)

    def test_superuser_can_delete_tasks_not_created_by_him(self):
        self.create_user("some_user", "user@email.com", "password")
        self.login("some_user", "password")
        self.app.get("/tasks", follow_redirects=True)
        self.post_task("My ordinary user task")
        self.app.get("/users/logout", follow_redirects=True)
        self.create_superuser("admin", "admin@admin.com", "password")
        self.login("admin", "password")
        self.app.get("/tasks", follow_redirects=True)
        response = self.app.get("/tasks/delete/1", follow_redirects=True)
        self.assertIn("Task has been deleted", response.data)
        task = db.session.query(Task).all()
        self.assertEquals([], task)

    def test_username_and_user_role_is_display_afert_login(self):
        self.create_user("some_user", "user@email.com", "password")
        self.login("some_user", "password")
        response = self.app.get("/tasks", follow_redirects=True)
        self.assertIn("some_user", response.data)
        self.assertIn("Your role is user", response.data)

    def test_no_task_modify_links_for_tasks_not_created_by_users(self):
        self.create_user("some_user", "user@email.com", "password")
        self.login("some_user", "password")
        self.app.get("/tasks", follow_redirects=True)
        self.post_task(task_name="Test task")
        self.logout()
        self.create_user("another_user", "another@user.com", "password")
        self.login("another_user", "password")
        response = self.app.get("/tasks", follow_redirects=True)
        self.assertNotIn("Mark as complete", response.data)
        self.assertNotIn("Delete task", response.data)

    def test_users_can_see_task_modify_links_only_for_their_tasks(self):
        self.create_user("some_user", "user@email.com", "password")
        self.login("some_user", "password")
        self.app.get("/tasks", follow_redirects=True)
        self.post_task(task_name="Test task")
        self.logout()
        self.create_user("another_user", "another@user.com", "password")
        self.login("another_user", "password")
        self.app.get("/tasks", follow_redirects=True)
        response = self.post_task(task_name="Test task2")
        self.assertIn("tasks/mark/2", response.data)
        self.assertIn("tasks/delete/2", response.data)
        self.assertNotIn("tasks/mark/1", response.data)
        self.assertNotIn("tasks/delete/1", response.data)

    def test_admin_users_can_see_all_tasks_modify_links(self):
        self.create_user("some_user", "user@email.com", "password")
        self.login("some_user", "password")
        self.app.get("/tasks", follow_redirects=True)
        self.post_task(task_name="Test task")
        self.logout()
        self.create_user("another_user", "another@user.com", "password")
        self.login("another_user", "password")
        self.app.get("/tasks", follow_redirects=True)
        self.post_task(task_name="Test2 task2")
        self.logout()
        self.create_superuser("superuser", "super@user.com", "password")
        self.login("superuser", "password")
        response = self.app.get('/tasks', follow_redirects=True)
        self.assertIn("tasks/mark/2", response.data)
        self.assertIn("tasks/delete/2", response.data)
        self.assertIn("tasks/mark/1", response.data)
        self.assertIn("tasks/delete/1", response.data)

    def test_404_error(self):
        response = self.app.get("/this-route-does-not-exist")
        self.assertEquals(404, response.status_code)
        self.assertIn('Sorry. There is nothing here', response.data)

    def test_500_error(self):
        bad_user = User(name="Tomek", email="tomek@bad.pl",
                        password="password")
        db.session.add(bad_user)
        db.session.commit()
        response = self.login("Tomek", "password")
        self.assertEquals(500, response.status_code)
        self.assertNotIn("ValueError: Invalid salt", response.data)
        self.assertIn("Something went terribly wrong", response.data)
        # =================================================================== #

if __name__ == "__main__":
    unittest.main()
