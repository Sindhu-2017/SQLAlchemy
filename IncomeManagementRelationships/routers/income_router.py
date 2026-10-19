from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
    File, 
    UploadFile,
    Body
)
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.income_service import IncomeService
from schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomePatch,
    IncomeResponse,
    IncomeActionResponse,
    IncomePaginatedResponse,
    IncomeFileUploadResponse
)

from exceptions.income_exceptions import(
    InvalidIncomeOperationError,
    IncomeNotFoundError
)

router = APIRouter(
    prefix = "/api/income",
    tags = ["Income"]
)

def get_income_service(db: Session = Depends(get_db)) -> IncomeService:
    return IncomeService(db)

IncomeServiceDependency = Annotated[IncomeService,Depends(get_income_service)]

@router.get("/",response_model=IncomePaginatedResponse)
def get_all_income(
    service: IncomeServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 5,
    income_name: Annotated[str | None,Query(min_length=1)] = None
):
    return service.get_incomes(page=page,page_size=page_size,income_name=income_name)


@router.get("/{income_id}",response_model=IncomeResponse)
def get_one_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        return service.get_income(income_id)
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) 
