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

  prompt = PromptTemplate(
      template="Break down the learning goal into smaller learning goals using Blooms taxonomy verbs: \n{format_instructions}\n{learning_goal}\n",
      input_variables=["learning_goal"],
      partial_variables={"format_instructions": parser.get_format_instructions()},
  )

  chain = prompt | model | parser
  return chain.invoke({"learning_goal": learning_goal})

def get_categories(learning_goal: str, roadmap_item_name: str, roadmap_item_description: str):
  model = ChatOpenAI()

  class Category(BaseModel):
     name: str
     description: str

  class Categories(BaseModel):
      categories: List[Category]
  
  parser = JsonOutputParser(pydantic_object=Categories)

  prompt = PromptTemplate(
      template="A user has the learning goal `{learning_goal}` and is focused on `{roadmap_item_description}`. Break down what they're focused on into a list of categories. Keep the category names short since they will be used on buttons:\n{format_instructions}\n",
      input_variables=["learning_goal", "roadmap_item_name", "roadmap_item_description"],
      partial_variables={"format_instructions": parser.get_format_instructions()},
  )

  chain = prompt | model | parser
  return chain.invoke({
     "learning_goal": learning_goal, 
     "roadmap_item_name": roadmap_item_name, 
     "roadmap_item_description": roadmap_item_description
     })