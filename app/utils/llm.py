from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from typing import List

from app import schemas


def get_roadmap(learning_goal: str):
    model = ChatOpenAI()

    class Topic(BaseModel):
        title: str
        description: str

    class StudyPlan(BaseModel):
        learning_goal: str
        title: str
        modules: List[Topic]

    parser = JsonOutputParser(pydantic_object=StudyPlan)

    prompt = PromptTemplate(
        template="Create a study plan by listing all the topics required to master the learning goal. The title should describe the topic (ex. 'Basic Music Theory'). The description should give more info on the topic (ex. Understanding notes, scales, and rhythm): \n{format_instructions}\n{learning_goal}\n",
        input_variables=["learning_goal"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser
    return chain.invoke({"learning_goal": learning_goal})


def get_submodules(module: schemas.roadmap_schema.Module):
    model = ChatOpenAI()

    class Submodule(BaseModel):
        title: str
        description: str
        search_query_to_find_learning_resources: str

    class Module(BaseModel):
        title: str
        submodules: List[Submodule]

    parser = JsonOutputParser(pydantic_object=Module)

    prompt = PromptTemplate(
        template="Break down the learning module into submodules which will be used to search for learning resources. Keep titles short since they will go on buttons.\n{format_instructions}\n{module}\n",
        input_variables=["module"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser
    module = chain.invoke({"module": module})
    return module["submodules"]


def get_query_to_find_learning_resources(roadmap_title: str, module_description: str, submodule_description: str):
    model = ChatOpenAI()

    class LearnResourcesQuery(BaseModel):
        learnResourcesQuery: str

    parser = JsonOutputParser(pydantic_object=LearnResourcesQuery)

    prompt = PromptTemplate(
        template="A user is learning the following. Create a search query that will be used to find learning resources for the sub module.\n{format_instructions}\nStudy plan: {roadmap_title}\nModule: {module_description}\n Sub module: {submodule_description}",
        input_variables=["roadmap_title",
                         "module_description", "submodule_description"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | model | parser
    query = chain.invoke({"roadmap_title": roadmap_title, "module_description": module_description,
                         "submodule_description": submodule_description})

    return query["learnResourcesQuery"]
