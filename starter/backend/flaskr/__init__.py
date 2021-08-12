from logging import FATAL
import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.base import NO_ARG
from sqlalchemy.sql.elements import Null

from sqlalchemy.sql.expression import select

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Displays only 10 questions per page
def paginate_question(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  formatted_questions = [question.format() for question in selection]
  current_questions = formatted_questions[start:end]

  return current_questions

def create_app(test_config=None):
  # Creates and configure the app
  app = Flask(__name__)
  setup_db(app)
  # Setups CORS to allow Cross Origin Resource Sharing
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    return response
  
  # Gets the categories from the database
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.id).all()
    # Formats the categories into a dictionary {id:type}
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories': len(categories)
    })

  # Gets all questions from the database 
  @app.route('/questions')
  def retrieve_questions():
    # Gets all questions
    selection = Question.query.order_by(Question.id).all()
    # Gets only 10 questions per page
    current_questions = paginate_question(request, selection) 
    # Gets all categories
    categories = Category.query.order_by(Category.id).all()
    # Formats the categories into a dictionary {id:type}
    formatted_categories = {category.id: category.type for category in categories}

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': formatted_categories,
      'current_category': None
    })

  # Delete a question by its id and after deleting displays the questions updated
  @app.route('/questions/<int:question_id>/delete', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id==question_id).one_or_none()
      
      if question is None:
        abort(404)
      
      question.delete()

      questions = Question.query.order_by(Question.id).all()

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': paginate_question(request, questions),
        'total_questions': len(questions)
      })
    except:
      abort(422)
  
  # Creates a new question and add into the database 
  @app.route('/questions', methods=['POST'])
  def create_question():
    question = request.get_json()['question']
    answer = request.get_json()['answer']
    category = request.get_json()['category']
    difficulty = request.get_json()['difficulty']
    
    try:
      question_item = Question(
        question=question,
        answer=answer,
        category=category,
        difficulty=difficulty)
      question_item.insert()

      return jsonify({
        'success': True,
        'created': question_item.id,
      })
    except:
      abort(422)
  
  # Searches for a question by its searchTerm passed by json from the search form 
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    try:
      # Gets the searchTerm from the form
      search = request.get_json()['searchTerm']
      # Gets all questions that have the same searchTerm in the title
      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
      # Format the questions to show only 10 per page
      current_questions = paginate_question(request, selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection.all()),
        'current_category': None
      })
    except:
      abort(422)
  
  # Gets the questions by its category, only displays questions with the same category
  @app.route('/categories/<int:category_id>/questions')
  def questions_by_category(category_id):
    try:
      selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
      current_questions = paginate_question(request, selection)
      current_category = Category.query.filter(Category.id == category_id).one_or_none()
      category = current_category.format()

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'current_category': [value for key, value in category.items()][1]
      })
    except:
      abort(422)
  
  # Gets the questions from the database randomly to play the quiz
  @app.route('/quizzes', methods=['POST'])
  def play():
    # Gets the quiz category and the previous questions to not repeat them
    quiz_category = request.get_json()['quiz_category']
    previous_questions = request.get_json()['previous_questions']

    try:
      category_id = int(quiz_category['id']) + 1

      # Gets the questions by the category selected
      if quiz_category['id'] == 0:
        quiz = Question.query.all()
      
      else:
        quiz = Question.query.filter(Question.category == category_id).all()

      question_selected = []

      # Checks if the question have not been picked yet
      for question in quiz:
        if question.id not in previous_questions: 
          question_selected.append(question.format())

      # Selects a random question from the list of questions 
      if len(question_selected) != 0:
        result = random.choice(question_selected)
        return jsonify({
          'question': result
        })
      else:
        return jsonify({
          'question': False
        })
    except:
      abort(422)

  # Error handlers 
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404
  
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400
  
  @app.errorhandler(500)
  def internal_server(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    })
  
  return app

    