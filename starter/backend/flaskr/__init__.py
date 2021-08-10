import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy.sql.expression import select

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_question(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  formatted_questions = [question.format() for question in selection]
  current_questions = formatted_questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories': len(categories)
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_question(request, selection) 
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': formatted_categories,
      'current_category': None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>/delete', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id==question_id).one_or_none()
    question.delete()

    questions = Question.query.order_by(Question.id).all()

    return jsonify({
      'success': True,
      'deleted': question_id,
      'questions': paginate_question(request, questions),
      'total_questions': len(questions)
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    question = request.get_json()['question']
    answer = request.get_json()['answer']
    category = request.get_json()['category']
    difficulty = request.get_json()['difficulty']
    
    question_item = Question(question=question, answer=answer, category=category, difficulty=difficulty)
    question_item.insert()

    return jsonify({
      'success': True,
      'created': question_item.id,
    })
    
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search = request.get_json()['searchTerm']
    selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
    current_questions = paginate_question(request, selection)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection.all())
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def questions_by_category(category_id):
    selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
    current_questions = paginate_question(request, selection)

    return jsonify({
      'success': True,
      'questions': current_questions
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play():
    quiz_category = request.get_json()['quiz_category']
    previous_questions = request.get_json()['previous_questions']

    category_id = int(quiz_category['id']) + 1

    if quiz_category['id'] == 0:
      quiz = Question.query.all()
    
    else:
      quiz = Question.query.filter(Question.category == category_id).all()

    question_selected = []

    for question in quiz:
      if question.id not in previous_questions: 
        question_selected.append(question.format())

    if len(question_selected) != 0:
      result = random.choice(question_selected)
      return jsonify({
        'question': result
      })
    else:
      return jsonify({
        'question': False
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    