from logging import FATAL
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import QUESTIONS_PER_PAGE, create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    # Set up the app
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','rockstar01','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Some question',
            'answer': 'Some answer',
            'category': 1,
            'difficulty': 3
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    # Endpoint tests

    # Categories endpoint
    def test_get_paginated_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))

    # Questions endpoint
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    # Questions endpoint page that does not exists
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    # Questions endpoint with the delete method
    def test_delete_question(self):
        res = self.client().delete('/questions/5/delete')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 5).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 5)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(question, None)
    
    # Questions endpoint trying to delete a question that doesn't exists
    def test_422_question_dont_exist(self):
        res = self.client().delete('/questions/1000/delete')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    # Questions endpoint with method post to create a question
    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    # Questions/search endpoint to search for a question
    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    # Questions/search endpoint case where the questions is not found
    def test_if_not_found_any_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'ttttttttttttt'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    # Categories/1/questions endpoint to look for questions by its category
    def test_gets_question_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 'Science')
    
    # Categories/9/questions endpoint where the category doesn't exist 
    def test_get_unexistent_category(self):
        res = self.client().get('/categories/9/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    # Quizzes endpoint to play the game and get a question that haven't appeared yet
    def test_get_quiz_question(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'type': 'History', 'id': 4}, 'previous_questions': [2]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
    
    # Quizzes endpoint to play the game with the json data being passed in a wrong way
    def test_422_quiz_question_fails(self):
        res = self.client().post('/quizzes', json={'quiz_category': 0, 'previous_questions': [2]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()