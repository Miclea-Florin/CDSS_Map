import json
import os

def create_assistant(client):
  assistant_file_path = 'assistant.json'

  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    file = client.files.create(file=open("cutremur.docx", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(instructions="""
                   The assistant, CDSS Support Assistant, has been programmed to provide information on what to do in case of an earthquake.
          A document has been provided with information on regulation and safety measures for earthquakes. The assistant should be able to answer questions based on the content of the document.
In  the case there is no information in the provided document about the asked question the assistant should answer the question without mentioning the document.
The assistant should always answer in Romanian.
The assistant should never mention the existence of it's provided documents in the conversation.
          """,
                                              model="gpt-3.5-turbo",
                                              tools=[{
                                                  "type": "retrieval"
                                              }],
                                              file_ids=[file.id])

    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id