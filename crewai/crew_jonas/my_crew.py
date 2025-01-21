from crewai import Agent, Crew, Task, Process
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import List
from crewai.project import CrewBase, crew, task, agent
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

