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
def create_pad(pad: schemas.PadCreate, db: Session = Depends(database.get_db)):
    db_pad = db.query(models.Pad).filter(models.Pad.title == pad.title).first()
    if db_pad:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Pad title already used")
    db_pad = models.Pad(title = pad.title, content = pad.content)
    db.add(db_pad)
    db.commit()
    db.refresh(db_pad)
    return db_pad

@app.get("/view-pads/", response_model = list[schemas.Pad])
def view_pads(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    pads = db.query(models.Pad).offset(skip).limit(limit).all()
    return pads

@app.get("/view-pads/{title}", response_model = schemas.Pad)
def search_pads(title: str, db: Session = Depends(database.get_db)):
    db_pad = db.query(models.Pad).filter(models.Pad.title == title).first()
    if db_pad is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Pad not found")
    return db_pad

@app.patch("/update-note/", response_model = schemas.Pad)
def update_note(title: str, pad: schemas.PadUpdate, db: Session = Depends(database.get_db)):
    db_pad = db.query(models.Pad).filter(models.Pad.title == title).first()
    if db_pad is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No pad with this title")
    if pad.title is not None:
        db_pad.title = pad.title
    if pad.content is not None:
        db_pad.content = pad.content
    else:
        if pad.backspace_num is not None:
            if pad.backspace_num < 0:
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Number or backspaces cannot be negative")
            chars_kept = max(0, len(db_pad.content) - pad.backspace_num)
            db_pad.content = db_pad.content[:chars_kept]
        if pad.content_add is not None:
            db_pad.content = db_pad.content + pad.content_add
    db.add(db_pad)
    db.commit()
    db.refresh(db_pad)
    return db_pad

@app.delete("/delete-pad/")
def delete_pad(title: str, db: Session = Depends(database.get_db)):
    db_pad = db.query(models.Pad).filter(models.Pad.title == title).first()
    if db_pad is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Pad not found")
    db.delete(db_pad)
    db.commit()
    return {"success" : "pad deleted"}