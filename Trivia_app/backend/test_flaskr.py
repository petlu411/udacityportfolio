import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # 1 -> Test for GET for questions (incl. pagination)
    def test_get_paginated_question(self): # Test Cleared
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))



    # 2 -> Test for DELETE question
    def test_delete_question(self):
        res = self.client().delete('/questions/25')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 25).one_or_none()
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],25)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question,None)

    #Another test could be to try to delete an out-of-bounds question, say index 1000. This should generate an error.

    # 3 -> Test for POST a new question (question, answer text, category, difficulty score)

    def test_post_new_question(self):
        res = self.client().post('/questions', json={'question':'What is a snake?','answer':'An animal','category':'3','difficulty':3},headers={'Content-Type':'application/json'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

        # One could imaging the json being incomplete, this should generate an error. 
 
    # 4 -> POST endpoint to get questions based on a search term

    def test_get_question_search_term_with_result(self):
        res = self.client().post('/questions',json={'search':'Who discovered penicillin?'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_get_question_search_term_without_result(self):
        res = self.client().post('/questions',json={'search':'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])

    # 5 -> GET endpoint to get questions based on category

    def test_get_question_from_category(self):
        res = self.client().get('/questions?category=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_get_question_based_on_category_out_of_bounds(self):
        res = self.client().get('/questions?category=10000')
        data = json.loads(res.data)
        print("---------------------..................................................")
        print(data)
        print(res.status_code)
        print("---------------------..................................................")
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['Message'],'Resource not found')    

    # 6 -> POST This endpoint should take category and previous question parameters and return a random questions within the given category,

    def test_get_question_from_category_and_prev_q(self):
        res = self.client().post('/quizzes?quiz_category=1&previous_questions=4')
        data = json.loads(res.data)        

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['question']))
        self.assertTrue(data['total_questions'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()