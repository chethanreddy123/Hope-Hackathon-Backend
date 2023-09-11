from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from loguru import logger
from pdf2image import convert_from_path
from fastapi import FastAPI, UploadFile, File
from langchain.llms import GooglePalm
from langchain import PromptTemplate, HuggingFaceHub, LLMChain
import json
import easyocr
from typing import List

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize OCR reader
reader = easyocr.Reader(['en'])

# Initialize GooglePalm
Palm = GooglePalm(temperature=0, 
                 model="models/text-bison-001", 
                 google_api_key="AIzaSyA1fu-ob27CzsJozdr6pHd96t5ziaD87wM")


# Initialize LLMChain
template = '''Extract the desired information from the following passage.

Only extract the properties mentioned in the 'information_extraction' function.

Passage:
{raw_text}

schema = {{
    "properties" : {{
        "name" : {{"type" : "string"}},
        "email" : {{"type" : "string"}},
        "age" : {{"type" : "string"}},
        "height" : {{"type" : "integer"}},
        "weight" : {{"type" : "integer"}},
        "phone" : {{"type" : "integer"}},
        "gender" : {{"type" : "string"}},
        "address" : {{"type" : "string"}}
    }},
    "required" : ["name" , "email" , "age" , "height" , "weight" , "phone" , "gender" , "address"]
}}

Note: If values or not extracted Make them ''.
'''


prompt = PromptTemplate(template=template, input_variables=["raw_text"])
llm_chain = LLMChain(prompt=prompt, llm=Palm)

properties = {
    'base_url': "https://na-1-dev.api.opentext.com",
    'css_url': "https://css.na-1-dev.api.opentext.com",
    'tenant_id': "86581e21-636f-4e1d-8336-061ddcd9293a",
    'username': "aioverflow.ml@gmail.com",
    'password': "!$hQPPh7HJnpC.7",
    'client_id': "eph2Is82hQZ6ltgrP4NjLgBuM96261Fv",
    'client_secret': "0p5Pz6MaHEThN1MV"
}

def process_pdf(file_path):
    logger.info(file_path)
    images = convert_from_path("mypdf.pdf", 500,poppler_path=file_path)
    for i, image in enumerate(images):
        fname = 'image'+str(i)+'.png'
        image.save(fname, "PNG")
    raw_string = ""
    for i, image in enumerate(images):
        image.save(f'page{i}.jpg', 'JPEG')
        result = reader.readtext(f'page{i}.jpg')
        labels = [bbox_label[1] for bbox_label in result]
        raw_string += ' '.join(labels)
    return raw_string

def get_auth_token():
    print("...Requesting New Authentication Token")

    url = f"{properties['base_url']}/tenants/{properties['tenant_id']}/oauth2/token"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'client_id': properties['client_id'],
        'client_secret': properties['client_secret'],
        'grant_type': "client_credentials",
        'username': properties['username'],
        'password': properties['password']
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if not response.ok:
            print("Error acquiring authentication token")
            print("Authentication Failed. Please verify your credentials in properties.py")
            return

        data = response.json()
        return data['access_token']

    except Exception as e:
        print(f"An error occurred: {e}")

def handle_upload_to_risk_guard(accessToken, file):
    piiData = ""
    piiDataPlaceholder = ""
    tmeResults = ""

    if not accessToken:
        print("Missing Authentication Token")
        return

    print("...Processing Text Mining")

    formData = {'File': ('sample.pdf', open('sample.pdf', 'rb'), 'application/pdf')}

    headers = { 
        'Authorization': f'Bearer {accessToken}', 
        'Accept': 'application/json'
    }

    response = requests.post(
        f'{properties["base_url"]}/mtm-riskguard/api/v1/process',
        headers=headers,
        files=formData
    )

    if response.status_code == 200:
        data = response.json()
        if not data.get('results', {}).get('tme', {}).get('result'):
            print("...No searchable PII data found")
            return
        print(f'...{data["header"]["status"]["description"]}')
        tmeResults = data
        return tmeResults
    elif response.status_code == 401:
        print("...Authentication Token has expired. Please obtain a new token.")
    else:
        print(f'...Error: {response.text}')
            
def display_pii_data(tme_results):
    pii_data = ""
    pii_data_placeholder = ""

    if len(tme_results) == 0:
        pii_data_placeholder = "...No PII data to display"
    else:
        for extracted_term in tme_results:
            cartridge_id = extracted_term['CartridgeID']
            subterm_value = extracted_term['Subterms']['Subterm'][0]['value']
            pii_data += f'{cartridge_id} = {subterm_value}\n'

    return pii_data


def save_pdf_file(file, filename):
    # Save the uploaded file as 'sample.pdf'
    with open(filename, "wb") as pdf_file:
        pdf_file.write(file.read())

@app.post("/process_upload/")
async def process_upload(file: UploadFile = File(...)):
    access_token = get_auth_token()
    if not access_token:
        return JSONResponse(content={"error": "Error acquiring authentication token"}, status_code=500)

    # Get the file name
    file_name = file.filename

    # If the file is not in PDF format, save it as sample.pdf
    if not file_name.endswith('.pdf'):
        with open('sample.pdf', 'wb') as f:
            f.write(await file.read())
        file_name = 'sample.pdf'

    logging.info(f"Processing file: {file_name}")
    logging.info("access_token: " + access_token)

    tme_results = handle_upload_to_risk_guard(access_token, file_name)
 

    return tme_results


@app.post("/extract_info/")
async def extract_info(files: List[UploadFile] = File(...)):
    extracted_info = []

    for uploaded_file in files:
        file_extension = uploaded_file.filename.split(".")[-1]
        
        # Save the uploaded file
        file_path = f"uploads/{uploaded_file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(uploaded_file.file.read())
        
        if file_extension.lower() in ['png', 'jpg', 'jpeg']:
            result = reader.readtext(file_path)
            labels = [bbox_label[1] for bbox_label in result]
            raw_string = ' '.join(labels)
        elif file_extension.lower() == 'pdf':
            raw_string = process_pdf(file_path)
            pass
        else:
            return {"error": "Unsupported file format"}
        
        # Run LLMChain
        res = llm_chain.run(raw_string)
        info = json.loads(res)
        extracted_info.append(info)
    
    return {"extracted_info": extracted_info}


