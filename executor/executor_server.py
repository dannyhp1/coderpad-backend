import executor_utils as eu

import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def main():
  return 'Welcome to the homepage of the executor.'

@app.route('/execute', methods = ['POST'])
def execute():
  language = request.form['language']
  code = request.form['code']
  
  # Call executor_utils to run code.
  print('API called with code %s in %s.' % (code, language))
  result = eu.build_and_execute(code, language)
  print(result)

  return jsonify({
    'build': result['build'],
    'run': str(result['run']),
    'error': str(result['error'])
  })

if __name__ == '__main__':
  app.run(debug=True)