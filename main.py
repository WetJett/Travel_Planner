import uvicorn
from fastapi import FastAPI

from database import engine, SessionLocal, Base
from models import Project, Place
from pydantic import BaseModel
from typing import List, Optional


Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI()

# Схема для місця (те, що приходить в запиті)
class PlaceCreate(BaseModel):
    external_id: str
    name: str

# Схема для проекту (те, що приходить в запиті)
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    places: List[PlaceCreate] # Список місць


@app.post("/projects/")
def create_project(project_data: ProjectCreate):
    db = SessionLocal()
    # Створюємо об'єкт (він ще не в базі)
    new_project = Project(name=project_data.name, description=project_data.description)
    
    db.add(new_project)
    db.commit() # Комітимо проект
    db.refresh(new_project) # Тепер у new_project є ID
    
    # Додаємо місця
    for p_data in project_data.places:
        new_place = Place(
            external_id=p_data.external_id, 
            name=p_data.name, 
            project_id=new_project.id
        )
        db.add(new_place)
    
    db.commit() # Комітимо місця
    
    # Зберігаємо ID перед закриттям сесії
    project_id = new_project.id
    
    db.close() # Закриваємо сесію тільки тут
    
    return {"message": "Project created", "id": project_id}
'''
@app.post("/projects/")
def create_project(project_data: ProjectCreate):
    db = SessionLocal()
    
    # Create project
    new_project = Project(name=project_data.name, description=project_data.description)
    db.add(new_project)
    db.commit()
    db.refresh(new_project) # Fetching ID of project
    
    # Adding places, link them to project_id
    for p_data in project_data.places:
        new_place = Place(
            external_id=p_data.external_id, 
            name=p_data.name, 
            project_id=new_project.id
        )
        db.add(new_place)
    
    db.commit()
    db.close()
    return {"message": "Project created", "id": new_project.id}'''


if __name__ == "__main__":
    uvicorn.run(app)