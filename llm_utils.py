import json
import os

def create_assistant(client):
    assistant_file_path = 'assistant.json'
    
    # Define the paths for the three document files
    doc_files = ['cutremur.docx', 'incendiu.docx', 'inundatie.docx']
    file_ids = []

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Upload each document and collect their file IDs
        for doc_file in doc_files:
            if os.path.exists(doc_file):
                file_upload = client.files.create(file=open(doc_file, "rb"), purpose='assistants')
                file_ids.append(file_upload.id)
            else:
                print(f"Error: {doc_file} does not exist.")
        
        # Ensure we have all necessary file IDs
        if len(file_ids) == len(doc_files):
            # Create the assistant with all document files attached
            assistant = client.beta.assistants.create(
                instructions="""
                    The assistant, CDSS Support Assistant, has been programmed to provide information on what to do in case of an earthquake, fire or flood.
                    A document has been provided with information on regulation and safety measures for earthquakes, fires or floods. The assistant should be able to answer questions based on the content of the document.
                    In the case there is no information in the provided documents about the asked question the assistant should answer the question without mentioning the document.
                    The assistant should always answer in Romanian.
                    The assistant should never mention the existence of its provided documents in the conversation.
                """,
                model="gpt-3.5-turbo",
                tools=[{"type": "retrieval"}],
                file_ids=file_ids
            )

            with open(assistant_file_path, 'w') as file:
                json.dump({'assistant_id': assistant.id}, file)
                print("Created a new assistant and saved the ID.")

            assistant_id = assistant.id
        else:
            print("Not all documents could be uploaded.")

    return assistant_id
