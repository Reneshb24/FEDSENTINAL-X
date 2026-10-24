import os
import tempfile
from pathlib import Path
import numpy as np
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.storage.models import Base, Dataset, Hospital, User
from backend.services.dataset_service import DatasetService
from backend.schemas.dataset import DatasetCreate, DatasetLinkImportRequest


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    hospital = Hospital(
        id="h-test-01",
        code="H01",
        name="Test Hospital",
        status="ACTIVE",
        security_status="TRUSTED",
        is_eligible=True,
    )
    user = User(
        id="u-test-01",
        email="test@h01.local",
        password_hash="fakehash",
        role="HOSPITAL_ADMIN",
        hospital_id="h-test-01",
        is_active=True,
    )
    session.add(hospital)
    session.add(user)
    session.commit()

    yield session
    session.close()


def test_import_version_from_synthetic_link(test_db):
    dataset = DatasetService.create_dataset(
        test_db,
        hospital_id="h-test-01",
        actor_user_id="u-test-01",
        payload=DatasetCreate(
            name="Clinical EHR Images",
            dataset_type="IMAGE_CLASSIFICATION",
            sample_count=0,
            num_classes=10,
        ),
    )

    version, size, fingerprint, classes = DatasetService.import_version_from_link(
        test_db,
        hospital_id="h-test-01",
        actor_user_id="u-test-01",
        dataset_id=dataset.id,
        version_name="v1-demo",
        record_link="demo://synthetic_records",
    )

    assert version.version == "v1-demo"
    assert version.sample_count == 200
    assert len(fingerprint) == 64
    assert size > 0


def test_import_version_from_local_npz_link(test_db):
    dataset = DatasetService.create_dataset(
        test_db,
        hospital_id="h-test-01",
        actor_user_id="u-test-01",
        payload=DatasetCreate(
            name="Clinical NPZ Dataset",
            dataset_type="IMAGE_CLASSIFICATION",
            sample_count=0,
            num_classes=10,
        ),
    )

    with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as f:
        tmp_name = f.name
        rng = np.random.RandomState(99)
        images = rng.randn(50, 1, 28, 28).astype(np.float32)
        labels = rng.randint(0, 10, size=(50,)).astype(np.int64)
        np.savez_compressed(tmp_name, images=images, labels=labels)

    try:
        version, size, fingerprint, classes = DatasetService.import_version_from_link(
            test_db,
            hospital_id="h-test-01",
            actor_user_id="u-test-01",
            dataset_id=dataset.id,
            version_name="v2-local",
            record_link=tmp_name,
        )

        assert version.version == "v2-local"
        assert version.sample_count == 50
        assert classes == 10
        assert len(fingerprint) == 64
    finally:
        Path(tmp_name).unlink(missing_ok=True)
