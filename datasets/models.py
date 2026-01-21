from pydantic import BaseModel
from typing import List, Dict

class DatasetRow(BaseModel):
    input_prompt: str
    expected_output: Dict
    metadata: Dict

class Dataset(BaseModel):
    dataset_name: str
    intent: str
    agent_type: str
    rows: List[DatasetRow]
    evaluation_rules: Dict
