import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
    page = request.args.get('page',1,type=int)
    start= (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    try:
      questions = [question.format() for question in selection]
    except:
      questions = [selection.format()]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app) # , resources={r"/api/*":{"origins":"*"}}
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    #reponse.headers.add('Access-Control-Allow-Origins','*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,PATCH,DELETE,OPTIONS')
    return response
  '''
  @TODO:  #DONE
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  #DONE
  @app.route('/categories',methods= ['GET'])
  def retrieve_categories():
    categories = Category.query.order_by(Category.id).all()
    if len(categories)==0:
      abort(404)
    formatted_categories = [category.format() for category in categories]
    print(formatted_categories)

    return jsonify({
      'success':True,
      'categories':formatted_categories
      #'total_categories': len(Category.query.all())
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
  #DONE
  @app.route('/questions',methods= ['GET']) 
  def retrieve_questions():
    category_id = request.args.get('category',None,type=int)
    categories = Category.query.distinct().all()
    selected_categories = [category.format() for category in categories]
    if category_id:
      if len(Category.query.all())<category_id:
        abort(404)
      
      category_type = Category.query.filter(Category.id == category_id).first().type

      questions = Question.query.filter(Question.category == str(category_id)).first()
      if questions is None:
        abort(404)
      selected_questions = paginate_questions(request,questions)

      return jsonify({
        'success':True,
        'questions':selected_questions,
        'category':category_id,
        'total_questions': len(Question.query.all())
      })
  
    else:
      questions = Question.query.order_by(Question.id).all()
      selected_questions = paginate_questions(request,questions)
      if len(questions)==0:
        abort(404)

      return jsonify({
        'success':True,
        'questions':selected_questions,
        'category': category_id,
        'categories': selected_categories,
        'total_questions': len(Question.query.all())
      })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def remove_question(question_id):
    question = Question.query.filter(Question.id == question_id).first()
    if not question is None:
      question.delete()
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request,selection)
    return jsonify({
        'success':True,
        'deleted':question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
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
  @app.route('/questions',methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question',None)
    new_answer = body.get('answer',None)
    new_category = body.get('category',None)
    new_difficulty = body.get('difficulty',None)
    search = body.get('search',None)
    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        current_questions = paginate_questions(request,selection)
        return jsonify({
          'success':True,
          'questions':current_questions,
          'category': "1",
          'total_questions':len(Question.query.all())
        })
      else:
        question = Question(question = new_question,answer = new_answer, category = new_category, difficulty = new_difficulty)
        question.insert()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request,selection)
        return jsonify({
          'success':True,
          'created':question.id,
          'questions':current_questions,
          'total_questions': len(Question.query.all())
        })
    except:
      abort(422)




  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

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


  @app.route('/quizzes',methods=['POST'])
  def get_random_q():
    print("I am in.")
    old_questions = request.args.get('previous_questions')
    category_id = request.args.get('quiz_category')
    print("--------------")
    print(old_questions)
    print("-------------")
    print(category_id)
    if old_questions is None and category_id is None:
      questions = Question.query.all()
    elif category_id is None and old_questions is not None:
      questions = Question.query.filter(Question.id != old_question_id).all()
    elif category_id is not None and old_questions is None:
      questions = Question.query.filter(Question.category == str(category_id)).all()
    else:
      questions = Question.query.filter(Question.id != old_question_id, Question.category == str(category_id)).all()
    chosen_question = random.choice(questions)

        #selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request,chosen_question)
    print (str(current_questions[0]['id'])+' '+current_questions[0]['question'])
    return jsonify({
      'success' : True,
      'question': chosen_question.format(),
      'total_questions':len(questions)
    })

  '''
  @TODO: #DONE
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #DONE
  @app.errorhandler(404) 
  def not_found(error):
    return jsonify({
      'success': False,
      'error' : 404,
      'Message': 'Resource not found'
    }),404

  @app.errorhandler(422)
  def unprocessed_entity(error):
    return jsonify({
      'success': False,
      'error' : 422,
      'Message' : 'This is a strange error. It seems something is unprocessed.'
    }),422


  return app

    