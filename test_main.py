#!/home/tomek/.envs/flask/bin/python
import os
import unittest
from datetime import date

from project import app, db
from config import BASE_DIR
from project.models import Task


TEST_DB = 'test.db'


class MainTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
            BASE_DIR, TEST_DB
        )
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # ======================== helpers ====================================== #
    def add_tasks(self):
        db.session.add(Task(name="Take my clothes off",
                            due_date=date(2015, 1, 22),
                            posted_date=date(2014, 10, 15), priority=10,
                            status=1, user_id=1))
        db.session.commit()

        db.session.add(Task(name="Be gentle and overpowered",
                            due_date=date(2016, 1, 22),
                            posted_date=date(2014, 12, 31), priority=7,
                            status=1, user_id=1))
        db.session.commit()

    # ========================= test views ================================== #
    def test_collection_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/tasks', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn('Take my clothes off', response.data)
        self.assertIn('Be gentle and overpowered', response.data)

    def test_resouce_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/task/2', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertNotIn('Take my clothes off', response.data)
        self.assertIn('Be gentle and overpowered', response.data)
        response = self.app.get('api/task/121', follow_redirects=True)
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn("There is nothing here", response.data)

if __name__ == '__main__':
    unittest.main()
