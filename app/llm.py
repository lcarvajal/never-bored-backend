from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from typing import List

def get_roadmap(learning_goal: str):
  model = ChatOpenAI()

  class LearningGoal(BaseModel):
      id: int
      name: str
      description: str

  class StudyPlan(BaseModel):
      modules: List[LearningGoal]
      learning_goal: str
  
  parser = JsonOutputParser(pydantic_object=StudyPlan)

  # A chat template converts raw user input into better input for an llm.
  prompt = PromptTemplate(
      template="Break down the learning goal into smaller learning goals using Blooms taxonomy verbs: \n{format_instructions}\n{learning_goal}\n",
      input_variables=["learning_goal"],
      partial_variables={"format_instructions": parser.get_format_instructions()},
  )

  chain = prompt | model | parser
  return chain.invoke({"learning_goal": learning_goal})