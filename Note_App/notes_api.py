from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from . import notes_db as database, notes_models as models, notes_schemas as schemas

@asynccontextmanager
async def lifespan(app : FastAPI):
    print("Starting App")
    models.Base.metadata.create_all(bind = database.engine)
    yield
    print("Closing App")

app = FastAPI(lifespan = lifespan)

@app.get("/")
def welcome_page():
    return {"message" : "Welcome to the note taking app!"}

@app.post("/create-pad/", response_model = schemas.Pad, status_code = status.HTTP_201_CREATED)
def create_pad(pad: schemas.PadBase, db: Session = Depends(database.get_db)):
    db_pad = db.query(models.Pad).filter(models.Pad.title == pad.title, models.Pad.is_active == True).first()
    if db_pad:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Pad title already used")
    db_pad = models.Pad(title = pad.title, content = pad.content, is_active = True)
    db.add(db_pad)
    db.commit()
    db.refresh(db_pad)
    return db_pad

@app.get("/view-pads/", response_model = list[schemas.Pad])
def view_pads(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    pads = db.query(models.Pad).filter(models.Pad.is_active == True).offset(skip).limit(limit).all()
    return pads

@app.get("/view-pads/{title}", response_model = schemas.Pad)
def search_pads(title: str, db: Session = Depends(database.get_db)):
    db_pad = db.query(models.Pad).filter(models.Pad.title == title, models.Pad.is_active == True).first()
    if db_pad is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Pad not found")
    return db_pad

@app.patch("/update-note/", response_model = schemas.Pad)
def update_note(title: str, pad: schemas.PadUpdate, db: Session = Depends(database.get_db)):
    db_pad = db.query(models.Pad).filter(models.Pad.title == title, models.Pad.is_active == True).first()
    if db_pad is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No pad with this title")
    if pad.title is not None and pad.title != db_pad.title:
            existing_active_pad = db.query(models.Pad).filter(
                models.Pad.title == pad.title, 
                models.Pad.is_active == True,
                models.Pad.id != db_pad.id # Exclude the current pad
            ).first()
            if existing_active_pad:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New title already used by another active pad")
            db_pad.title = pad.title
    if pad.content is not None:
        db_pad.content = pad.content
    db.add(db_pad)
    db.commit()
    db.refresh(db_pad)
    return db_pad

@app.delete("/delete-pad/")
def delete_pad(title: str, db: Session = Depends(database.get_db)):
    db_pad = db.query(models.Pad).filter(models.Pad.title == title, models.Pad.is_active == True).first()
    if db_pad is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Pad not found")
    db_pad.is_active = False
    db.add(db_pad)
    db.commit()
    db.refresh(db_pad)
    return {"success" : "pad deleted"}
