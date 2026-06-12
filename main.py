import uvicorn
from fastapi import FastAPI

from database import engine, SessionLocal, Base
from models import Project, Place
from pydantic import BaseModel
from typing import List, Optional


Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI()


class PlaceCreate(BaseModel):
    external_id: str
    name: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    places: List[PlaceCreate] 


@app.post("/projects/")
def create_project(project_data: ProjectCreate):
    db = SessionLocal()
    
    new_project = Project(name=project_data.name, description=project_data.description)
    
    db.add(new_project)
    db.commit() 
    db.refresh(new_project) # new_project has ID now
    
    for p_data in project_data.places:
        new_place = Place(
            external_id=p_data.external_id, 
            name=p_data.name, 
            project_id=new_project.id
        )
        db.add(new_place)
    
    db.commit() 
    project_id = new_project.id
    db.close() 
    
    return {"message": "Project created", "id": project_id}

@app.get("/projects/")
def get_projects():
    db = SessionLocal()
    projects = db.query(Project).all()
    db.close()
    return projects

@app.get("/projects/{project_id}")
def get_project(project_id: int):
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == project_id).first()
    db.close()
    return project

if __name__ == "__main__":
    uvicorn.run(app)