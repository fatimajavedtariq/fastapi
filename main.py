from fastapi import FastAPI, Path, HTTPException, Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal

app = FastAPI() 

from pydantic import BaseModel, EmailStr, field_validator, model_validator, computed_field

from typing import List, Dict

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the patient', example='P002')]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City of the patient')]
    age: Annotated[int, Field(..., description='Age of the patient', gt=0, lt=120)]
    gender: Annotated[str, Literal['male', 'female', 'others'], Field(..., description='gender of the patient')]
    height: Annotated[float, Field(..., description='Height of the patient in mtrs', gt=0)]
    weight: Annotated[float, Field(..., description='Weight of the patient in kgs', gt=0)]

    @computed_field
    @property 
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property 
    def verdict(self) -> str:
        if self.bmi<18.5:
          return 'underweight'
        elif self.bmi<24.9:
          return 'normal'
        elif self.bmi<29.9:
           return 'overweight'
        elif self.bmi<34.9:
           return 'obese' 

def load_data():
  with open('patients.json', 'r') as p:
    data = json.load(p)
    return data

def save_data(data):
   with open('patients.json','w') as p:
      json.dump(data, p)

@app.get("/")
def home():
  return {'message': 'Patient Management System API'}

@app.get('/about')
def about():
  return {'message': "A fully functional API to manage your patient records"}

@app.get('/view')
def view():
  data = load_data()
  return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str =  Path(..., description='ID of the patient in the DB', example='POO1')):
  data = load_data()
  if patient_id in data:
    return data[patient_id]
  raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description="Sort on the basis of height, weight or bmi"), order: str = Query('asc', description="Sort in asc or desc order" )):
    valid_fields = ["height", 'weight', 'bmi']

    if sort_by not in valid_fields:
      raise HTTPException(status_code=400, detail=f"Invalid field select from {valid_fields}")
    
    if order not in ['asc', 'desc']:
      raise HTTPException(status_code=400, detail="Invalid order, select between asc and desc")
    
    data = load_data()
    order_by = True if order=='desc' else False
    sorted_data=sorted(data.values(), key= lambda x: x.get(sort_by, 0), reverse=order_by)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
   data = load_data()

   if patient.id in data:
      raise HTTPException(status_code=404, detail='Patient already exists')
   
   data[patient.id] = patient.model_dump(exclude='id')

   save_data(data)

   return JSONResponse(content='Data Entered')


      
   