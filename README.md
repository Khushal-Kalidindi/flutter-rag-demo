# Flutter RAG Demo

This is a demo for a chatbot which uses Retrieval Augmented Generation(RAG), demonstrated during my guest lecture for ITP-368 Programming Graphical User Interfaces at University of Southern California. The aim of the lecture is to introduce undergraduate students to making Gen AI applications in Flutter. 

### Technologies used
- Flutter
- ChatGPT
- Pinecone Vector DB
- Firebase

# Demo Setup

## Virtual Environment
1. **Activate Virtual Environment**:
   - On macOS/Linux:
     ```sh
     source env/bin/activate
     ```
   - On Windows:
     ```sh
     env\Scripts\activate
     ```

2. **Install Dependencies**:
   After activating the virtual environment, install the project dependencies:
   ```sh
   pip install -r requirements.txt

## Setup .env File

### Create .env File

Copy the `.env_sample` file to a new `.env` file:
```sh
cp .env_sample .env
```

### Add Your API Keys

Edit the `.env` file and replace the placeholders with your actual values:
- **OPENAI_KEY**: You can get your OpenAI API key by visiting OpenAI's API Key page. https://openai.com/index/openai-api/
- **PINECONE_KEY**: You can get your Pinecone API key by signing up or logging in to Pinecone. https://www.pinecone.io/
- **PINECONE_INDEX**: Specify the name of the Pinecone index you want to retrieve data from. You can manage your indices via the Pinecone Dashboard.
- **DATA_FOLDER**: Specify the path to the data folder that you want to load into the index.

After adding your keys and index information, save the `.env` file.

## Usage for `python-db.py`

The `python-db.py` script can be used for two main operations: loading data into Pinecone and querying data from Pinecone.

### Load Data into Pinecone

To load data from your specified data folder into the Pinecone index, run the script with the `-L` flag:
```sh
python python-db.py -L
```

### Query Data from Pinecone

To query data from Pinecone, run the script with the `-Q` flag followed by your query:
```sh
python python-db.py -Q "<your-query>"
```

#### Example

To load data:
```sh
python python-db.py -L
```

To query data with the query "What is AI?" from a Pinecone index called "example-index":
```sh
python python-db.py -Q "What is AI?" example-index
```

## Setup Flutter Frontend

### Copy .env to Flutter Frontend

Copy the `.env` file into the `flutter_frontend` directory:
```sh
cp .env flutter_frontend/.env
```

### Change Directory to Flutter Frontend

Navigate to the `flutter_frontend` directory:
```sh
cd flutter_frontend
```

### Run Flutter Application

Run the Flutter application:
```sh
flutter run
```

