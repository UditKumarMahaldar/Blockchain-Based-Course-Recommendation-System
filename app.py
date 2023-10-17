import numpy as np
import pandas as pd
from web3 import Web3
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from flask import Flask, render_template, request

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='recommendation.log', level=logging.DEBUG)

# Connect to the local Ethereum blockchain
try:
    w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))
    assert w3.is_connected(), "Not connected to the local Ethereum blockchain"
except Exception as e:
    logging.error(f"Error connecting to the Ethereum blockchain: {e}")
    print("Error connecting to the Ethereum blockchain")
    exit()

# Set up the contract
try:
    contract_abi = [
        {
            "inputs": [
                {
                    "internalType": "string",
                    "name": "_courseName",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "_difficultyLevel",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "_courseDescription",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "_skills",
                    "type": "string"
                }
            ],
            "name": "addCourse",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                }
            ],
            "name": "courses",
            "outputs": [
                {
                    "internalType": "string",
                    "name": "courseName",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "difficultyLevel",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "courseDescription",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "skills",
                    "type": "string"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "index",
                    "type": "uint256"
                }
            ],
            "name": "getCourse",
            "outputs": [
                {
                    "internalType": "string",
                    "name": "",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "",
                    "type": "string"
                },
                {
                    "internalType": "string",
                    "name": "",
                    "type": "string"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "getCourseCount",
            "outputs": [
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    contract_address = w3.to_checksum_address('0xe66b356A2Dd452F3E53C1D54a470C31FB26eDD4e')
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
except Exception as e:
    logging.error(f"Error setting up the contract: {e}")
    print("Error setting up the contract")
    exit()

# Set up the TF-IDF vectorizer and PorterStemmer
tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
ps = PorterStemmer()


def preprocess_course(course_data):
    # Preprocess the course data
    course_name, difficulty_level, course_description, skills = course_data
    course_name = course_name.replace(',', ' ')
    course_name = course_name.replace(':', '')
    course_description = course_description.replace(',', ' ')
    course_description = course_description.replace('_', '')
    course_description = course_description.replace(':', '')
    course_description = course_description.replace('(', '')
    course_description = course_description.replace(')', '')
    skills = skills.replace('(', '')
    skills = skills.replace(')', '')
    tags = f"{course_name} {difficulty_level} {course_description} {skills}"
    tags = tags.lower()
    tags = ' '.join([ps.stem(word) for word in tags.split()])
    return course_name, tags


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Get the input course name from the form data
        course_name = request.form['course_name']

        # Fetch all the courses from the smart contract
        course_count = contract.functions.getCourseCount().call()
        courses = [contract.functions.getCourse(i).call() for i in range(course_count)]

        # Preprocess the courses and create a DataFrame
        preprocessed_courses = [preprocess_course(course) for course in courses]
        data = pd.DataFrame(preprocessed_courses, columns=['course_name', 'tags'])

        # Find the index of the input course
        course_index = data[data['course_name'] == course_name].index[0]

        # Vectorize the tags using the TF-IDF vectorizer
        vectors = tfidf.fit_transform(data['tags']).toarray()

        # Compute the cosine similarity between the vectors
        similarity = cosine_similarity(vectors)

        # Find the most similar courses
        distances = similarity[course_index]
        course_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]

        # Get the recommended course names
        recommended_courses = [contract.functions.getCourse(i[0]).call()[0] for i in course_list]

        # Render the results page with the recommended courses
        return render_template('results.html', course_name=course_name, recommended_courses=recommended_courses)
    except Exception as e:
        logging.error(f"Error generating recommendations: {e}")
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
