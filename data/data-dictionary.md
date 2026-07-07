# SRAG Data Dictionary

> Version: 1.0
> Dataset: SRAG 2019–2026 (SIVEP-Gripe)
> Purpose: Document the CSV columns used by the application and provide a human-readable mapping for developers and AI agents.

---

# Overview

The official SRAG dataset contains nearly one hundred columns describing severe acute respiratory syndrome notifications.

Our application does **not** use every available field. Instead, we focus on the information required for analytics, charts, dashboards and AI-generated reports.

Each field is classified as one of the following:

| Status | Meaning |
|---------|---------|
| Core | Used by the application and AI reports |
| Secondary | Stored but currently unused |
| Ignored | Not imported into the application |

---

# Notification

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| NU_NOTIFIC | Notification ID | 0 | Core | Unique notification identifier |
| DT_NOTIFIC | Notification Date | 1 | Core | Date the notification was created |
| DT_SIN_PRI | Symptom Onset Date | 3 | Core | Date symptoms began |

---

# Patient

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| CS_SEXO | Sex | 10 | Core | Patient sex |
| DT_NASC | Birth Date | 11 | Secondary | Used to calculate age when necessary |
| NU_IDADE_N | Age | 12 | Core | Patient age |
| TP_IDADE | Age Unit | 13 | Secondary | Years, months or days |
| CS_RACA | Race | 16 | Secondary | Patient race |
| CS_ESCOL_N | Education | 18 | Ignored | Not relevant for current reports |

---

# Location

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| SG_UF | State | 21 | Core | Brazilian state of residence |
| SG_UF_NOT | State of Notification | 5 | Secondary | State where the case was notified (may differ from residence) |
| ID_MUNICIP | Municipality | 8 | Core | Municipality name |
| ID_REGIONA | Health Region | 6 | Secondary | Health region |

---

# Symptoms

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| FEBRE | Fever | 29 | Core | Patient had fever |
| TOSSE | Cough | 30 | Core | Patient had cough |
| GARGANTA | Sore Throat | 31 | Core | Patient had sore throat |
| DISPNEIA | Dyspnea | 32 | Core | Difficulty breathing |
| DESC_RESP | Respiratory Distress | 33 | Core | Respiratory distress |
| SATURACAO | Low Oxygen Saturation | 34 | Core | O₂ saturation below 95% |
| DIARREIA | Diarrhea | 35 | Secondary | Gastrointestinal symptom |
| VOMITO | Vomiting | 36 | Secondary | Gastrointestinal symptom |
| FADIGA | Fatigue | 125 | Secondary | General fatigue |
| PERD_OLFT | Loss of Smell | 126 | Secondary | COVID symptom |
| PERD_PALA | Loss of Taste | 127 | Secondary | COVID symptom |

---

# Comorbidities

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| CARDIOPATI | Heart Disease | 41 | Core | Cardiopathy |
| DIABETES | Diabetes | 46 | Core | Diabetes |
| ASMA | Asthma | 45 | Core | Asthma |
| OBESIDADE | Obesity | 51 | Core | Obesity |
| PNEUMOPATI | Lung Disease | 48 | Core | Chronic lung disease |
| RENAL | Kidney Disease | 50 | Core | Chronic kidney disease |
| IMUNODEPRE | Immunosuppression | 49 | Core | Immunodeficiency |
| NEUROLOGIC | Neurological Disease | 47 | Secondary | Neurological disorders |
| HEMATOLOGI | Hematologic Disease | 42 | Secondary | Blood disorders |
| HEPATICA | Liver Disease | 44 | Secondary | Liver disease |

---

# Hospitalization

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| HOSPITAL | Hospitalized | 68 | Core | Hospital admission |
| DT_INTERNA | Admission Date | 69 | Core | Hospital admission date |
| UTI | ICU Admission | 76 | Core | ICU required |
| DT_ENTUTI | ICU Entry Date | 77 | Secondary | ICU admission |
| DT_SAIDUTI | ICU Exit Date | 78 | Secondary | ICU discharge |
| SUPORT_VEN | Ventilatory Support | 79 | Core | Ventilation support |
| NM_UN_INTE | Hospital Name | 75 | Ignored | Not required for analytics |

---

# Laboratory Tests

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| CLASSI_FIN | Final Classification | 107 | Core | Final diagnosis |
| PCR_SARS2 | SARS-CoV-2 PCR | 120 | Core | COVID PCR result |
| PCR_VSR | RSV PCR | 96 | Secondary | RSV detection |
| PCR_RINO | Rhinovirus PCR | 104 | Secondary | Rhinovirus detection |
| PCR_METAP | Metapneumovirus PCR | 102 | Secondary | Metapneumovirus |
| PCR_FLUASU | Influenza A | 91 | Core | Influenza A subtype |
| PCR_FLUBLI | Influenza B | 93 | Core | Influenza B |

---

# Vaccination

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| VACINA_COV | COVID Vaccinated | 158 | Core | COVID vaccination status |
| DOSE_1_COV | First Dose | 159 | Secondary | First dose date |
| DOSE_2_COV | Second Dose | 160 | Secondary | Second dose date |
| DOSE_REF | Booster Dose | 161 | Secondary | Booster date |
| FAB_COV_1 | Vaccine Manufacturer | 165 | Secondary | Vaccine manufacturer |

---

# Outcome

| CSV Field | Friendly Name | Index | Status | Description |
|------------|---------------|--------|--------|-------------|
| EVOLUCAO | Outcome | 110 | Core | Cure or death |
| DT_EVOLUCA | Outcome Date | 111 | Secondary | Outcome date |

---

# Enumerations

## Boolean

| Value | Meaning |
|---------|----------|
| 1 | Yes |
| 2 | No |
| 9 | Unknown |

---

## Sex

| Value | Meaning |
|---------|----------|
| M | Male |
| F | Female |

---

## Final Classification

| Value | Meaning |
|---------|----------|
| 1 | Influenza |
| 2 | Other Respiratory Virus |
| 3 | Other Etiological Agent |
| 4 | Unspecified SRAG |
| 5 | COVID-19 |

---

## Outcome

| Value | Meaning |
|---------|----------|
| 1 | Cure |
| 2 | Death caused by SRAG |
| 3 | Death by another cause |

---

# Fields Used by the AI

The AI assistant is allowed to use the following information when generating reports:

- Notification date
- Symptom onset date
- State
- Municipality
- Age
- Sex
- Symptoms
- Comorbidities
- Hospitalization
- ICU admission
- Ventilatory support
- Laboratory diagnosis
- Final classification
- Vaccination status
- Outcome

Personally identifiable information, hospital names, addresses and administrative metadata are intentionally excluded from prompts.

---

# Future Candidates

The following fields are good candidates for future versions:

- Pregnancy
- Ethnicity
- Education
- Occupation
- Health Region
- Hospital stay duration
- ICU duration
- Antiviral treatment
- Imaging results
- Detailed laboratory exams
