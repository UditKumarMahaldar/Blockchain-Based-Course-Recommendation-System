import pandas as pd
from web3 import Web3

# Connect to the local Ethereum blockchain
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))
assert w3.is_connected(), "Not connected to the local Ethereum blockchain"

# Set up the contract
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

# Set up the account for transactions
private_key = '68be17f089658f2a6f6fc6e94d2dc780c035de79dd6a6f87e248b1819f4af41d'
account = w3.eth.account.from_key(private_key)
w3.eth.defaultAccount = account.address

# Read the CSV file
courses_df = pd.read_csv(r"E:\RESEARCH\RECOMMENDED SYSTEM\archive\Coursera.csv")

# Iterate through the CSV rows and add course details to the blockchain
for index, row in courses_df.iterrows():
    course_name = row['Course Name']
    difficulty_level = row['Difficulty Level']
    course_description = row['Course Description']
    skills = row['Skills']

    # Estimate the gas required for the transaction
    gas_estimate = contract.functions.addCourse(course_name, difficulty_level, course_description, skills).estimate_gas()

    # Create and sign the transaction
    transaction = contract.functions.addCourse(course_name, difficulty_level, course_description, skills).build_transaction({
        'gas': gas_estimate,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
    })
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print(f"Transaction sent for course {course_name}, waiting for confirmation...")

    # Wait for the transaction to be mined
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"Course {course_name} added to the blockchain")