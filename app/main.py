from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.admin import router as admin_router
from app.controllers.election import router as election_router
from app.controllers.election_invite import router as election_invite_router
from app.controllers.vote import router as vote_router
from app.db.config import Base, engine
from app.db.seed import seed_admin_user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Votos anonimos - Backend Blockchain",
    version="1.0.0",
    description="API para controle de eleições com votos secretos registrados na Blockchain (Polygon)."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/api", tags=["Acesso admin"])
app.include_router(election_router, prefix="/api", tags=["Elections"])
app.include_router(election_invite_router, prefix="/api",
                   tags=["Election Invites"])
app.include_router(vote_router, prefix="/api", tags=["Voting"])

seed_admin_user()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=3334, reload=True)
