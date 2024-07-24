from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from typing import List

from app import schemas

def get_roadmap(learning_goal: str):
  model = ChatOpenAI()

  class Module(BaseModel):
      title: str
      description: str

  class StudyPlan(BaseModel):
      learning_goal: str
      title: str
      modules: List[Module]
  
  parser = JsonOutputParser(pydantic_object=StudyPlan)

  prompt = PromptTemplate(
      template="Break down the learning goal into a study plan. First, list all the topics required to master the learning goal. Then organize them into modules: \n{format_instructions}\n{learning_goal}\n",
      input_variables=["learning_goal"],
      partial_variables={"format_instructions": parser.get_format_instructions()},
  )

  chain = prompt | model | parser
  return chain.invoke({"learning_goal": learning_goal})

def get_submodules(module: schemas.roadmap_schema.Module):
   model = ChatOpenAI()

   class Submodule(BaseModel):
      title: str
      description: str
      query_for_learning_resources: str
   
   parser = JsonOutputParser(pydantic_object=List[Submodule])

   prompt = PromptTemplate(
      template="Break down the learning module into submodules which will be used to search for learning resources. Keep titles short since they will go on buttons.\n{format_instructions}\n{module}\n",
      input_variables=["module"],
      partial_variables={"format_instructions": parser.get_format_instructions()},
   )

   chain = prompt | model | parser
   return chain.invoke({"module": module})

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