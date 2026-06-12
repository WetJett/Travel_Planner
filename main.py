import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException

from database import engine, SessionLocal, Base
from models import Project, Place
from pydantic import BaseModel
from typing import List, Optional

import requests


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


def validate_place_exists(external_id: str):
    url = f"https://api.artic.edu/api/v1/artworks/{external_id}"
    response = requests.get(url)
    return response.status_code == 200

@app.post("/projects/")
def create_project(project_data: ProjectCreate):
    db = SessionLocal()
    
    #Place quontity validation
    if len(project_data.places) < 1 or len(project_data.places) > 10:
        db.close()
        raise HTTPException(status_code=400, detail="Project must have between 1 and 10 places.")

    new_project = Project(name=project_data.name, description=project_data.description)
    db.add(new_project)
    db.commit() 
    db.refresh(new_project) 
    
    for p_data in project_data.places:
        # validation in API
        if not validate_place_exists(p_data.external_id):
            db.close() 
            raise HTTPException(status_code=404, detail=f"Place {p_data.external_id} not found in API")
        
        new_place = Place(
            external_id=p_data.external_id, 
            name=p_data.name, 
            project_id=new_project.id
        )
        db.add(new_place)
    
    db.commit() 
    db.close() 
    return {"message": "Project created", "id": new_project.id}

@app.get("/projects/")
def get_projects():
    db = SessionLocal()
    projects = db.query(Project).all()
    db.close()
    return projects

@app.get("/places/")
def get_places():
    db = SessionLocal()
    places = db.query(Place).all()
    db.close()
    return places

@app.get("/projects/{project_id}")
def get_project(project_id: int):
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == project_id).first()
    db.close()
    return project

@app.patch("/places/{place_id}/")
def update_place(place_id: int, notes: Optional[str] = None, is_visited: Optional[bool] = None):
    db = SessionLocal()
    place = db.query(Place).filter(Place.id == place_id).first()
    project = place.project
    
    if not place:
        db.close()
        raise HTTPException(status_code=404, detail="Place not found")

    if project.is_completed:
        raise HTTPException(status_code=400, detail="Cannot modify a completed project.")
    
    
    if notes is not None:
        place.notes = notes
    if is_visited is not None:
        place.is_visited = is_visited
        
    db.commit()
    db.refresh(place)
    
    
    all_visited = all(p.is_visited for p in project.places)
    
    if all_visited:
        project.is_completed = True
        db.commit()
    else:
        project.is_completed = False 
        db.commit()
        
    db.close()
    return {"message": "Place updated", "project_completed": project.is_completed}

@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        db.close()
        raise HTTPException(status_code=404, detail="Project not found")

    if any(p.is_visited for p in project.places):
        db.close()
        raise HTTPException(status_code=400, detail="Cannot delete project with visited places")
        
    db.delete(project)
    db.commit()
    db.close()
    return {"message": "Project deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app)