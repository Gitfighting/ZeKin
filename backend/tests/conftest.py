import pytest

import app.modules.all_models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.modules.seed import seed_reference_data


@pytest.fixture(autouse=True)
def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_reference_data(session)
