from pydantic import BaseModel, Field
from typing import Optional

class EpidemiologicalMetrics(BaseModel):
    total_cases: int
    total_deaths: int
    total_icu: int
    total_vaccinated: int
    mortality_rate: float
    icu_rate: float
    # Proportion of hospitalized SRAG patients who had COVID vaccination.
    # This is NOT a population-level vaccination rate (no IBGE denominators used).
    # It reflects vaccination status among inpatients only (field VACINA_COV).
    hospitalized_vaccination_rate: float = Field(
        ...,
        description=(
            "Percentage of hospitalized SRAG cases who had received COVID-19 "
            "vaccination (VACINA_COV=1). This is an inpatient cohort metric, "
            "not a population-level vaccination rate."
        )
    )
    case_increase_rate: float
    cases_last_30_days: Optional[int] = 0
    cases_prev_30_days: Optional[int] = 0
