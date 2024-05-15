def generate_quiz_prompt(
    number_fill_the_blanks, number_multiple_options, number_order_the_words
):
    message = f"""I am going to give you some images. This images are screen captures of a book. 
    I want you to understand them. 
    We are going to use the text on this images for a microlearning quiz app. The purpose is to generate questions.

There are different question types with their correspondent data shapes:

```
class AnswerNode:
    value: str
```
"""

    if number_fill_the_blanks > 0:
        message += f"""
You will need {number_fill_the_blanks} questions of type FILL_THE_BLANK, each should look like:
```
{{
    'id': 'uuid',
    'type': 'FILL_THE_BLANK',
    'question': 'String',
    'answer_options': [AnswerNode()],
    'correct_answer': int,  # index of answer_options with correct answer
    'correct_reason': 'String'
}}
```
"""

    if number_multiple_options > 0:
        message += f"""
You will need {number_multiple_options} questions of type MULTIPLE_OPTION, each should look like:
```
{{
    'id': 'uuid',
    'type': 'MULTIPLE_OPTION',
    'question': 'String',
    'answer_options': [AnswerNode()],
    'correct_answer': int,  # index of answer_options with correct answer
    'correct_reason': 'String'
}}
```
"""

    if number_order_the_words > 0:
        message += f"""
You will need {number_order_the_words} questions of type ORDER_THE_WORDS, each should look like:
```
{{
    'id': 'uuid',
    'type': 'ORDER_THE_WORDS',
    'question_text': 'Order the words to form a valid SQL query:',
    'answer_options': [
      {{ 'value': '*' }},
      {{ 'value': 'SELECT' }},
      {{ 'value': 'from' }},
      {{ 'value': 'Users' }},
    ],
    'correct_answer': [1, 0, 2, 3],  # array with the correct order of words
}}

Limit the question_text to 7 words max.
```
"""

    message += """
Create questions that will help test and remember the comprehension of the text.
Mix between question types.
I want only output as JSON (array of objects). No extra comments or suggestions.
"""

    return message
